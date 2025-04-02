import frappe 


def boot_session(bootinfo) :
    
    jofotara_settings = frappe.db.get_all("JoFotara  Settings" , {"enable_integration" : 1 } , pluck="company")
    bootinfo.jofotara_settings = jofotara_settings