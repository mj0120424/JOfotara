import frappe
from uuid import uuid4
from frappe import _dict
from frappe.utils import get_date_str
from frappe.model.document import Document
from jo_fotara.fotara.utils import format_number
from jo_fotara.fotara.classes.xml import FotaraXML
from jo_fotara.fotara.classes.validate import ValidateJofotaraInvoice


class JoFotaraData:
    
    def __init__(self ,company_info:Document , sales_invoice:Document):
        """
        Initialize ZatcaInvoiceData with sales invoice details.
        Handles fetching and validating necessary data.
        """
        self.jofotara_invoice = {}
        self.sales_invoice : _dict = sales_invoice
        self.company_info : _dict = company_info
        self.total_invoice_without_tax = 0.00
        self.total_discount_amount = 0.00
        self.total_taxes_and_charges = 0.00
        self.rate_include_tax = bool(filter(lambda x : x.get("included_in_print_rate") == 1 , self.sales_invoice.get("taxes") ))

        self.get_customer_details()
        self.validate_jofotara_invoice()
        self.handle_jofotara_data()
        self.create_jofotara_xml()


    def get_customer_details(self) :
        
        self.customer_info = frappe.db.get_value("Customer" , self.sales_invoice.get("customer") , [
            'name' , 'tax_id' , 'customer_type' , 'identification_types' , 'identification_value'
        ] , as_dict=True)
        
        customer_address = self.sales_invoice.get("customer_address")
        if not customer_address and self.customer_info.get("customer_type") == "Company":
            customer_address = frappe.db.get_value("Dynamic Link" , {"link_doctype": "Customer" , "link_name": self.sales_invoice.get("customer") , "parenttype": "Address"} , "parent") 
                
        self.customer_address = frappe.db.get_value("Address" , customer_address ,["country_subentity_code" , "pincode" , "phone" ] , as_dict=True) if customer_address else {}
    

    def validate_jofotara_invoice(self):
        obj = ValidateJofotaraInvoice(
            self.sales_invoice , 
            self.company_info,
            self.customer_info,
            self.customer_address
        )
    

    def create_jofotara_xml(self):
        """
        Creates an XML representation of the Zatca invoice.
        """
        self.xml = FotaraXML(self.jofotara_invoice)


    def handle_jofotara_data(self):
        """
        Handles the preparation of Zatca invoice data.
        """
        self.add_invoice_data()
        self.add_company_data()
        self.add_customer_data()
        self.add_invoice_items_data()
        self.add_global_discounts()
        self.add_invoice_totals_data()


    def add_invoice_data(self):
        """
        Add Invoice data to the Zatca invoice dictionary.
        """

        # Prepare invoice data using a dictionary
        invoice_data = {
            "ProfileID": "reporting:1.0",
            "Invoice-ID": self.sales_invoice.get("name", ""),
            "Invoice-UUID": str(uuid4()),
            "IssueDate": get_date_str(self.sales_invoice.get("posting_date")),
            "InvoiceTypeCode": "381" if self.sales_invoice.get("is_return") else "388" ,
            "InvoiceTypeCode-name": "012",
            "Note" : self.sales_invoice.get("remarks") or "No Remarks",
            "DocumentCurrencyCode": "JOD",
            "TaxCurrencyCode": "JOD",
            "CurrencySybmol" : "JO" ,
            "ICV": get_icv(self.sales_invoice.get("company")) ,
        }

        # Conditionally add fields based on invoice type
        if self.sales_invoice.get("is_return") :
            
            return_invoice = frappe.db.get_value("Sales Invoice" , self.sales_invoice.get("return_against") , ["uuid" , "grand_total"]  ,as_dict=True) 
            invoice_data["InvoiceDocumentReference-ID"] = self.sales_invoice.get("return_against") 
            invoice_data["BillingReference-UUID"] = return_invoice.get("uuid")
            invoice_data["DocumentDescription"] = str(return_invoice.get("grand_total"))
            invoice_data["InstructionNote"] = self.sales_invoice.get("reason_for_return", "") or "Return Invoice"
            invoice_data["PaymentMeansCode"] =  "10"

        # Add the invoice data to the Zatca invoice
        self.jofotara_invoice.update(invoice_data)


    def add_company_data(self):
        """
        Add Company data to the Zatca invoice dictionary.
        """
        self.jofotara_invoice["company"] = {
            "CompanyID": self.company_info.get("tax_id", ""),
            "RegistrationName": self.company_info.get("company_name_in_arabic", ""),
            "PartyIdentification-ID" : self.company_info.get("sequence_of_income_source")
        }
        

    def add_customer_data(self):
        """
        Add Customer data to the Zatca invoice dictionary.
        """

        customer_details = {
                "PartyIdentification-schemeID":  self.customer_info.get("identification_types", ""),
                "PartyIdentification-ID":  self.customer_info.get("identification_value", ""),
                "RegistrationName":  self.customer_info.get("name", ""),
                "IdentificationCode": "JO" ,
        }
        
        if pincode := self.customer_address.get("pincode") :
            customer_details["PostalZone"] = pincode
            
        if country_subentity_code := self.customer_address.get("country_subentity_code") :
            customer_details["CountrySubentityCode"] = country_subentity_code
            
        if phone := self.customer_address.get("phone") :
            customer_details["Telephone"] = phone
            
        if self.customer_info.get("customer_type") == "Company" :
            customer_details["CompanyID"] = self.customer_info.get("tax_id")
            
            
        self.jofotara_invoice["customer"] = customer_details
 
        
    def add_invoice_totals_data(self):
        """
        Add Invoice Totals to the Zatca invoice dictionary.
        """
        self.actual_grand_total = str(
            format_number(
                format_number(self.total_taxes_and_charges) + format_number(self.total_invoice_without_tax )
            )
        )
        # Add totals data to the Zatca invoice
        self.jofotara_invoice.update({
            "TaxExclusiveAmount": str(format_number(format_number(self.total_invoice_without_tax) + format_number(self.total_discount_amount) )), # Total Invoice Before Discount
            "TaxInclusiveAmount": self.actual_grand_total, # Total Invoice 
            "AllowanceTotalAmount": str(format_number(self.total_discount_amount)),
            "PrepaidAmount": "0",  # Assuming this is a constant value
            "PayableAmount": self.actual_grand_total, # Total Invoice 
        })


    def add_invoice_items_data(self):
        """
        Add Invoice Items to the Zatca invoice dictionary.
        """
        # Extract sales invoice with a fallback to an empty dictionary
        
        list_of_items = []
        tax_subtotals = {}
        
        calculated_items : list[dict] = self._get_items_calculation()
        
        for item in calculated_items :
            self.add_item_lines(item , list_of_items)
            # self.add_taxes_category(item , tax_subtotals)
         
        self.jofotara_invoice["taxes"] = {
            "TaxTotal-TaxAmount-BASE": str(format_number(self.total_taxes_and_charges )),
            "TaxTotal-TaxAmount": str(format_number(self.total_taxes_and_charges )),
            "TaxSubtotal": list(tax_subtotals.values())
        }
        
        self.jofotara_invoice["items"] = list_of_items
        
    def _get_items_calculation(self) :
        
        items : list = self.sales_invoice.get("items")
        
        if self.sales_invoice.get("items")[0].get("line_extension_amount")  in [None , "" , 0]  or  self.sales_invoice.get("update_fotara_calculation"):
            from jo_fotara.fotara.invoice import update_itemised_tax_data  
            update_itemised_tax_data(self.sales_invoice)
                
        return items

        
         

    def add_item_lines(self , item:dict , list_of_items:list ) :
        
        line_extension_amount = abs(item.get("line_extension_amount", 0))
        tax_amount = abs(item.get("tax_amount", 0))
        item_line = {
            "InvoiceLine-ID": str(item.get("idx", 0)),
            "InvoicedQuantity": str(abs(item.get("qty", 0))),
            "InvoicedQuantity-unitCode" : "PCE" ,
            "LineExtensionAmount": str(line_extension_amount),
            "TaxAmount": str(tax_amount),
            "RoundingAmount": str(abs(item.get("rounding_amount", 0))),
            "TaxSubtotal-TaxableAmount" : str(abs(item.get("line_extension_amount"))),
            "TaxSubtotal-TaxAmount" : str(abs(item.get("tax_amount", 0))),
            "TaxCategory-ID" : item.get("tax_category", ""),
            "TaxCategory-Percent" : str(item.get("tax_rate", 0)) ,
            "Name": item.get("item_name") or item.get("item_code"),
            "PriceAmount": str(abs(item.get("price_amount", 0))),
            "BaseQuantity" : "1",
        }
        
        self.total_invoice_without_tax += line_extension_amount
        self.total_taxes_and_charges += tax_amount

        if discount_amount := item.get("discount_amount", 0)  :
            total_discount_amount = format_number(abs(discount_amount * item.get("qty")))
            item_line["AllowanceCharge-Amount"] = str(total_discount_amount)
            item_line["AllowanceCharge-Indicator"] = "false"
            item_line["AllowanceCharge-Reason"] = "discount"
            self.total_discount_amount += total_discount_amount


        list_of_items.append(item_line)
        
        
    def add_taxes_category(self, item : dict , tax_subtotals:dict) :
        
        tax_category = "{0}_{1}".format(item.get("tax_category")  ,item.get("tax_rate"))

        if tax_category not in tax_subtotals:

            tax_subtotals[tax_category] = {
                'TaxableAmount' : abs(item.get("line_extension_amount") )  ,
                'Percent': "{0:.2f}".format(abs(item.get("tax_rate"))),
                'TaxCategory-ID': item.get("tax_category") ,
                "TaxAmount" : abs(item.get("tax_amount"))
            }
        else :
            tax_subtotals[tax_category]['TaxableAmount'] += format_number(abs(item.get("line_extension_amount")))
            tax_subtotals[tax_category]["TaxAmount"] += abs(item.get("tax_amount"))

            
    def add_global_discounts(self) :
        
        if self.total_discount_amount > 0 :
            self.jofotara_invoice["AllowanceCharge"] = {
                "ChargeIndicator" : "false" ,
                "AllowanceChargeReason" : "discount" ,
                "Amount" : str(format_number(self.total_discount_amount))
            }

# Back Again

def get_icv(company ) :
    
    InvoiceIncounter  = "1"
    
    sql_query = frappe.db.sql(""" 
         SELECT 
            icv  
        FROM `tabJoFotara Logs` 
        WHERE icv = (
            SELECT MAX(icv) 
            FROM `tabJoFotara Logs` 
            WHERE company = %(company)s
                AND status = "Success"
        )
    """,{
        "company" : company ,
    } ,as_dict=True)

    if sql_query :
        InvoiceIncounter =  str(sql_query[0].get("icv") + 1 )
        
    return  InvoiceIncounter
        
    