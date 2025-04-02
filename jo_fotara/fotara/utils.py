import io
import ast
import  frappe
from frappe.utils import flt
from pyqrcode import create as qr_create
from requests import post as make_post_request


# In Case Json In Js Not Converted Properly
def convert_json_if_not_format(string_data) :

    data_dict = ast.literal_eval(string_data)
    
    return data_dict



def send_invoice_to_fotara(company_settings:dict , invoice:str) :
    
    url = "https://backend.jofotara.gov.jo/core/invoices/"
    
    headers = {
        "Client-Id" : company_settings.get("client_id") ,
        "Secret-Key" : company_settings.get("client_secret") ,
        "Content-Type" : "application/json" ,
    }
    
    data = {
        "invoice" : invoice ,
    }
    
    
    return make_post_request(url,headers=headers , json=data)
    
    
    
def create_jofotara_logs(log:dict=None):
    
    if not log : return 
    
    zatca_log = frappe.new_doc("JoFotara Logs")
    zatca_log.update(log)
    zatca_log.flags.ignore_permissions = True
    zatca_log.flags.ignore_mandatory = True
    zatca_log.save()
    
    
    
def attach_qr_code(qrcode_base64, invoice_name):
    qr_image = io.BytesIO()
    url = qr_create(qrcode_base64, error='L')
    url.png(qr_image, scale=2, quiet_zone=1)

    # Saving QR Code image as a file

    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": f"JoFotara-{invoice_name}.png" ,
        "content": qr_image.getvalue(),
        "is_private": 0,
        "attached_to_doctype": "Sales Invoice",
        "attached_to_name": invoice_name ,
        "attached_to_field": "jofotara_qrcode"
    })
    _file.insert(ignore_permissions=True)
    
    return _file.file_url


def get_company_details_of_integration(company:str) -> dict:
    
    def get_jo_fotara_setting() :

        settings = {}
        if zatca_settings := frappe.db.exists("JoFotara  Settings" , {"company" : company , "enable_integration" : 1}) :
            settings = frappe.get_doc("JoFotara  Settings" , zatca_settings)
            
        return settings
            
    return frappe.cache.get_value("jofotara_info_{0}".format(company) , get_jo_fotara_setting)


def format_number(number):
    default_percision = frappe.get_cached_value("JoFotara Configration" , None ,"float_precision")

    return flt(number , precision=default_percision)