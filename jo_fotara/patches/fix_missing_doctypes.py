import frappe
from click import secho
from jo_fotara.utils import create_additional_fields


def execute() :
    
    if frappe.db.exists("Custom Field" , {"dt" : "Purchase Invoice Item" , "fieldname" : "tax_rate"} ) :
        return 
    
    # To Run Method Again For Old Company
    create_additional_fields()
    
    secho("Update Missing Doctype Fields For Taxes" , fg="green")