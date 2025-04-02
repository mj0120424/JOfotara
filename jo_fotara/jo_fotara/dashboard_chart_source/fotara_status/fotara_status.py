
import frappe
from frappe import _
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
# @cache_source
def get(
    chart_name=None,
    chart=None,
    no_cache=None,
    filters=None,
    from_date=None,
    to_date=None,
    timespan=None,
    time_interval=None,
    heatmap_year=None,
):
    conditions = ""
    
    filters = frappe.parse_json(filters) or {}
    default_company = filters.get("company") if filters.get("company") not in ["" , None] else frappe.defaults.get_defaults().get("company")
    if default_company : conditions += "AND company = %(company)s "

    sql_query = frappe.db.sql(""" 
                                                      
        SELECT 
            SUM(
                CASE 
                    WHEN status = "Success"
                    THEN 1
                    ELSE 0
                END 
            ) as success_log 
        FROM `tabJoFotara Logs` 
        WHERE 1=1
            {conditions}
                
    """.format(conditions=conditions) , {
        "company" : default_company,
    },as_dict=True)
    

    error_log = frappe.db.sql(""" 
        SELECT DISTINCT reference_name AS error_log , reference_doctype 
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
    """.format(conditions=conditions) , {
        "company" : default_company,
    },as_dict=True)
        
    
    values = [
        sql_query[0].get("success_log") if sql_query else 0 , 
        len(error_log)if error_log else 0 , 
    ]

    return {
    	"labels": [ _("Success") , _("Rejected") ],
    	"datasets": [{"name": _("Invoices Status"), "values": values}],
    	"type": "Pie",
    }