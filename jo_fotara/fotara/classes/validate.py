import frappe
from frappe import _

class ValidateJofotaraInvoice:
    
    def __init__(self,  sales_invoice , company_info ,  customer_info , customer_address ) :
        
        self.sales_invoice = sales_invoice
        self.company_info = company_info
        self.customer_info = customer_info
        self.customer_address = customer_address
        
        self.run_validation()
        
        
    def run_validation(self) :
        
        self.validate_sent_before()
        self.validate_sales_invoice()
        
        self.validate_company_info()
        self.validate_d_or_c_invoice()
        
        
    def validate_sales_invoice(self) :
        
        SalesInvoiceField = ["customer" ,"items" , "taxes"]
        
        for field in SalesInvoiceField :
            if self.sales_invoice.get(field) in ["" , None , []] :
                frappe.throw(title=_("Sales Invoice Error") , msg=_("{0} is Missing in Sales Invoice").format(frappe.bold(self.sales_invoice.meta.get_label(field))))
        
        if self.sales_invoice.get("discount_amount") > 0  : 
            frappe.throw(_("Fotara Not Support Discount In Global Invoice"))
            
        not_tax_category = [ None for item in self.sales_invoice.get("items") if item.get("tax_category") in ["" , None] ]
        if not_tax_category  :
            frappe.throw(_("Tax Category Missing In Sales Invoice Item"))
            

    def validate_sent_before(self) :
        
        if self.sales_invoice.get("uploaded_to_jofotara") :
            frappe.throw(_("Sales Invoice {0} Sent To Fotara Before").format(self.sales_invoice.get("name")))
            
        ListZatcaLogs = frappe.db.get_all("JoFotara Logs" , {
            "reference_doctype" : "Sales Invoice" , "reference_name" : self.sales_invoice.get("name") , "status" : ["in" , ["Success" , "Warning"]]
        })
        
        if ListZatcaLogs :
            frappe.throw(_("Sales Invoice {0} Sent To Fotara Before").format(self.sales_invoice.get("name")))
    
    
    def validate_company_info(self) :
        
        ListOfFileds = ["company_name_in_arabic", "tax_id" , "sequence_of_income_source" , "client_id" , "client_secret"]
        
        for field in ListOfFileds :
            if self.company_info.get(field) in [None , ""] :
                frappe.throw(_("Please Register Company {0} First").format(self.company_info.get("company")))
                
            
    def validate_d_or_c_invoice(self) :
        
        if  self.sales_invoice.get("is_return") == 1 :
            
            if not self.sales_invoice.get("reason_for_return") or not self.sales_invoice.get("return_against") :
                
                frappe.throw(title= _("Sales Invoice Data") , msg=_("In Case Return or Debit Note You Must Add Reason For Return and Return Against"))
            
            