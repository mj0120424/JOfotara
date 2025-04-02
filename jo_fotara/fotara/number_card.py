import json
import frappe
from frappe.utils import get_year_start , get_year_ending , nowdate

@frappe.whitelist()
def get_all_invoices_issued(filters) :
    
    filters = json.loads(filters)
    conditions = {
        "uploaded_to_jofotara" : 1 ,
        "is_return" : 0 ,
        "docstatus" : 1,
        "status" :["not in" , ["Return" , "Cancelled"]]
    }

    default_company = filters.get("company") if filters.get("company") not in ["" , None] else frappe.defaults.get_defaults().get("company")
    if default_company :  conditions["company"] = default_company 
    number_of_invoices = frappe.db.count("Sales Invoice" , conditions)
    
    return {
        "value": number_of_invoices,
        "fieldtype": "Int",
        "route_options": filters,
        "route": ["app", "sales-invoice"]
    }
    
    
@frappe.whitelist()
def get_invoices_issued_for_this_year(filters) :
    
    filters = json.loads(filters)
    conditions = {
        "uploaded_to_jofotara" : 1 ,
        "is_return" : 0 ,
        "docstatus" : 1,
        "status" :["not in" , ["Return" , "Cancelled"]],
        "posting_date" : ["between" , [get_year_start(nowdate()) , get_year_ending(nowdate())]]
    }
    
    default_company = filters.get("company") if filters.get("company") not in ["" , None] else frappe.defaults.get_defaults().get("company")
    if default_company :  conditions["company"] = default_company 
    number_of_invoices = frappe.db.count("Sales Invoice" , conditions)
    
    return {
        "value": number_of_invoices,
        "fieldtype": "Int",
        "route_options": filters,
        "route": ["app", "sales-invoice"]
    }
    
    
@frappe.whitelist()
def get_all_notifications_issued(filters) :
    
    filters = json.loads(filters)
    conditions = {
        "uploaded_to_jofotara" : 1 ,
        "is_return" : 1 ,
        "docstatus" : 1,
        "status" :["in" , ["Return" ]],
        "posting_date" : ["between" , [get_year_start(nowdate()) , get_year_ending(nowdate())]]
    }
    
    default_company = filters.get("company") if filters.get("company") not in ["" , None] else frappe.defaults.get_defaults().get("company")
    if default_company :  conditions["company"] = default_company 
    number_of_invoices = frappe.db.count("Sales Invoice" , conditions)

    return {
        "value": number_of_invoices,
        "fieldtype": "Int",
        "route_options": filters,
        "route": ["app", "sales-invoice"]
    }
    
@frappe.whitelist()
def get_total_invoice(filters) :
    
    filters = json.loads(filters)
    conditions = {
        "uploaded_to_jofotara" : 1 ,
        "docstatus" : 1,
    }
    
    default_company = filters.get("company") if filters.get("company") not in ["" , None] else frappe.defaults.get_defaults().get("company")
    if default_company :  conditions["company"] = default_company 
    number_of_invoices = frappe.db.count("Sales Invoice" , conditions)
    
    return {
        "value": number_of_invoices,
        "fieldtype": "Int",
        "route_options": filters,
        "route": ["app", "sales-invoice"]
    }