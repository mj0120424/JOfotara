# Copyright (c) 2025, Basel & Seleem and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters) :
    
    return [
        {
            "label" : _("Reference DocType") ,
            "fieldtype" : "Data" ,
            "fieldname" : "reference_doctype" ,
            "width" : 180
        },
        {
            "label" : _("Invoice") ,
            "fieldtype" : "Dynamic Link" ,
            "fieldname" : "invoice" ,
            "options" : "reference_doctype" ,
            "width" : 250
        },
    ]


def get_data(filters:dict) :
    
    conditions = ""
    
    if filters.get("company") : conditions += "AND company = %(company)s"
    
    sql_query = frappe.db.sql("""
        SELECT DISTINCT reference_name AS invoice , reference_doctype 
        FROM `tabJoFotara Logs` t1
        WHERE status = 'Error'
            {conditions}
            AND NOT EXISTS (
                SELECT 1
                FROM `tabJoFotara Logs` t2
                WHERE t2.reference_name = t1.reference_name
                    AND t2.status IN ('Success' , 'Warning')
                    {conditions}
            );
    """.format(conditions=conditions),{
        "company" : filters.get("company") ,
    } ,as_dict=True)
    
    return sql_query