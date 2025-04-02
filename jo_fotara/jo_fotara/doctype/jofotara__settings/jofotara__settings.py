# Copyright (c) 2025, Basel Waheed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class JoFotaraSettings(Document):
    
    # def validate(self) :
    #     self.validate_tax_id()
    
    
    # def validate_tax_id(self) :
        
    #     if len(self.tax_id) != 8 :
    #         frappe.throw(_("Tax ID Must Equal 8 Digits"))
	
 
    def before_save(self) :
        frappe.clear_document_cache(self.doctype , self.name)
        frappe.cache.delete_key("jofotara_info_{0}".format(self.company))
        
        if self.has_value_changed("enable_integration") :
            frappe.clear_cache()
