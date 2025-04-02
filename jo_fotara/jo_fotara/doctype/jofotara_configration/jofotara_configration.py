# Copyright (c) 2025, Basel Waheed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JoFotaraConfigration(Document):
	
 
	def before_save(self) :
		frappe.clear_document_cache(self.doctype , self.name)
		frappe.clear_cache()
		
