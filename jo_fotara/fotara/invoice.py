import json
import frappe
import base64
from frappe import _
from lxml import etree
from frappe.utils import flt
from jo_fotara.fotara.classes.data import JoFotaraData
from jo_fotara.fotara.utils import ( 
    attach_qr_code ,
    send_invoice_to_fotara ,
    create_jofotara_logs ,
    convert_json_if_not_format ,
    get_company_details_of_integration ,
    format_number,
)



@frappe.whitelist()
def resend_invoice(invoice_name):
    sales_invoice = frappe.get_doc("Sales Invoice", invoice_name)
    handle_company_integration(sales_invoice)


def send_invoice_after_submit(doc ,event) :
    handle_company_integration(doc)
    


def handle_company_integration(sales_invoice:dict) :
    
    company_info : dict = get_company_details_of_integration(sales_invoice.company)
    if not sales_invoice.get("uploaded_to_jofotara") and company_info :    
        send_invoice_to_jofotara(company_info , sales_invoice)


def send_invoice_to_jofotara(company_info , sales_invoice):
    
    invoice_data = JoFotaraData(company_info ,sales_invoice)
    xml_content = etree.tostring(invoice_data.xml.root, encoding='utf-8')
    invoice = base64.b64encode(xml_content).decode('utf-8')
    
    try:
        response = send_invoice_to_fotara(company_info , invoice)  
        handle_response(sales_invoice, invoice_data  , invoice , response)
         
    except Exception as e:
        frappe.msgprint(_("Error Please Call Administrator") , alert=True , indicator="red")
        frappe.log_error(title="JoFotara Application", reference_doctype="Sales Invoice" , reference_name= sales_invoice.name)

    return True

        
    
def handle_response(sales_invoice , invoice_data , invoice , response) :

    Response : dict = response.json() if response.status_code in [200 ,201 , 202] else {}
    if response.status_code in [200 ,201 , 202] :
        sales_invoice.db_set({
            "jofotara_status" :  Response.get("EINV_STATUS"),
            "uploaded_to_jofotara" : 1 ,
            "uuid" : invoice_data.jofotara_invoice.get("Invoice-UUID") ,
        } , commit=True)
        
        try :
            file_url = attach_qr_code(Response.get("EINV_QR") , sales_invoice.name)
            frappe.db.set_value("Sales Invoice" , sales_invoice.name , "jofotara_qrcode" , file_url)
            frappe.msgprint(_("Invoice Accepted in JoFotara") , alert=True , indicator="green")
        except Exception as e :
            frappe.log_error(title="JoFotara Application QR code", reference_doctype="Sales Invoice" , reference_name= sales_invoice.name)
            
    else :
        message = "Invoice Rejected in Fotara" if response.status_code == 400 else "Internal Server Error of Fotara Please Try Again Letter"
        frappe.msgprint(_(message) , alert=True , indicator="orange")
       
    create_jofotara_logs(
        dict(
            status= "Success" if response.status_code in [200 , 201 , 202] else "Error",
            uuid=invoice_data.jofotara_invoice.get("Invoice-UUID"),
            company= sales_invoice.get("company"),
            reference_doctype="Sales Invoice",
            reference_name= sales_invoice.name ,
            icv=invoice_data.jofotara_invoice.get("ICV"),
            response_text = response.text ,
            actual_grand_total = invoice_data.actual_grand_total ,
            
            url = response.url,
            headers = response.headers,
            invoice_encoded=invoice,
            
            # NEW Response From Jofotara
            einv_results = str(Response.get("EINV_RESULTS")) ,
            einv_status = Response.get("EINV_STATUS"),
            einv_num = Response.get("EINV_NUM"),
            einv_inv_uuid = Response.get("EINV_INV_UUID"),
            einv_singed_invoice = Response.get("EINV_SINGED_INVOICE"),
            einv_qr = Response.get("EINV_QR"),
            
            xml_content = etree.tostring(invoice_data.xml.root, encoding='utf-8'),
            response_xml = base64.b64decode(Response.get("EINV_SINGED_INVOICE")).decode(encoding="utf-8") if Response.get("EINV_SINGED_INVOICE") else ""
        )
    )




def update_itemised_tax_data(doc):
    if not doc.taxes: return
    
    itemised_tax = get_itemised_tax(doc.taxes)


    for idx , row in enumerate(doc.items , start=1):
        tax_rate = 0.0
        tax_amount = 0.00
        included_in_print_rate = 0

        if row.item_code and itemised_tax.get(row.item_code):

            for d, tax in itemised_tax.get(row.item_code).items() :
                tax_rate += tax.get('tax_rate', 0)
                tax_amount += tax.get("tax_amount")
                included_in_print_rate += tax.get("included_in_print_rate")

        row.tax_rate = flt(tax_rate, row.precision("tax_rate"))
         
        if included_in_print_rate :
            row.line_extension_amount = format_number(abs(row.base_net_amount))
            row.price_amount = format_number(abs(format_number(row.line_extension_amount / row.get("qty") )) + abs(row.get("discount_amount" , 0.00)))
            row.tax_amount = format_number(row.line_extension_amount * ( row.tax_rate / 100 ) ) 
            row.rounding_amount =  format_number(row.line_extension_amount + row.tax_amount )

        else :
            row.price_amount = row.price_list_rate or row.net_rate 
            row.line_extension_amount = format_number(abs( row.price_amount * row.get('qty') ) - abs(row.get("discount_amount" , 0.00)))
            row.tax_amount = format_number(row.line_extension_amount * ( row.tax_rate / 100 ) ) 
            row.rounding_amount = format_number(row.line_extension_amount + row.tax_amount )
        
        



# Not Handle Multi Currency

def get_itemised_tax(taxes):

    itemised_tax = {}
    for tax in taxes:
        if getattr(tax, "category", None) and tax.category == "Valuation":
            continue
        
        try :
            item_tax_map = json.loads(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
        except :
            item_tax_map = convert_json_if_not_format(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
  
        if item_tax_map:
            for item_code, tax_data in item_tax_map.items():
                itemised_tax.setdefault(item_code, frappe._dict())

                tax_rate = 0.0
                tax_amount = 0.0

                if isinstance(tax_data, list):
                    tax_rate = flt(tax_data[0])
                    tax_amount = flt(tax_data[1])
                else:
                    tax_rate = flt(tax_data)

                itemised_tax[item_code][tax.description] = frappe._dict(dict(
                    tax_rate=tax_rate, 
                    tax_amount=tax_amount , 
                    included_in_print_rate=tax.included_in_print_rate , 
                    tax_account = tax.account_head
                ))

    return itemised_tax



def check_cancellation_availability(doc , event) :
    
    if doc.get("uploaded_to_jofotara") == 1 :
        enable_cancel_invoice = frappe.get_cached_value("JoFotara Configration" , None , "enable_cancel_invoice")
        
        if not enable_cancel_invoice :
            frappe.throw(title=_("Fotara Permissions") , msg=_("You Don't have Permission To Cancel Invoice Sent to Fotara"))


def check_for_deletion(doc , event) :
    
    if doc.get("uploaded_to_jofotara") == 1:
        enable_delete_invoice = frappe.get_cached_value("JoFotara Configration" , None , "enable_delete_invoice")
        
        if not enable_delete_invoice :
            frappe.throw(title=_("Fotara Permissions") , msg=_("You Don't have Permission To Delete Invoice Sent to Fotara"))