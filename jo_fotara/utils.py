
import frappe
from click import secho
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


SellingFields = [
    {
        "fieldname": "tax_category",
        "label" : "Tax Category" ,
        "fieldtype" : "Link" ,
        "options" : "Tax Category" ,
        "insert_after": "item_tax_template",
        "read_only" : 1 ,
        "fetch_from" : "item_tax_template.tax_category",
        "fetch_if_empty" : 1 ,
    },
    {
        "fieldname" : "section_break101",
        "label" : "JoFotara Calculation" ,
        "fieldtype"  : "Section Break" ,
        "insert_after" : "grant_commission",
        "hidden" : 1,
    },
    {
        "fieldname" : "price_amount" ,
        "label" : "Price Amount" ,
        "fieldtype" : "Float" ,
        "insert_after" : "section_break101",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
    {
        "fieldname" : "line_extension_amount" ,
        "label" : "Line Extension Amount" ,
        "fieldtype" : "Float" ,
        "insert_after" : "price_amount",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
    {
        "fieldname" : "item_discount" ,
        "label" : "Item Discount" ,
        "fieldtype" : "Float" ,
        "insert_after" : "line_extension_amount",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
    {
        "fieldname" : "column_break1011" ,
        "fieldtype" : "Column Break" ,
        "insert_after" : "item_discount"
    },
    {
        "fieldname" : "tax_rate" ,
        "label" : "Tax Rate" ,
        "fieldtype" : "Float" ,
        "insert_after" : "column_break1011",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
    {
        "fieldname" : "tax_amount" ,
        "label" : "Tax Amount" ,
        "fieldtype" : "Float" ,
        "insert_after" : "tax_rate",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
    {
        "fieldname" : "rounding_amount" ,
        "label" : "Rounding Amount" ,
        "fieldtype" : "Float" ,
        "insert_after" : "tax_amount",
        "read_only" : 1 ,
        "hidden" : 1,
        "no_copy" : 1,
    },
] 


def after_app_install(app_name) :
    
    if app_name != "jo_fotara" : return 
    
    create_additional_fields()
    
    


def create_additional_fields() :
    
    custom_fields = {
        "Mode of Payment" : [
            {
                "fieldname" : "payment_code" ,
                "label" : "Payment Code" ,
                "fieldtype" : "Data" ,
                "insert_after" : "type" ,
                "description" : "Cash : 10 , Credit : 30 , Bank Account : 42 , Bank Card : 48"
            }  
        ],
        "Customer" : [ 
            {
                "fieldname": "identification_types",
                "label": "Identification Types",
                "fieldtype": "Link",
                "options": "Identification Types",
                "insert_after": "tax_id",
                "depends_on" : "" ,
                "mandatory_depends_on" : "eval: doc.customer_type == 'Company' "
            },
            {
                "fieldname": "identification_value",
                "label" : "Identification Value" ,
                "fieldtype" : "Data" ,
                "insert_after": "identification_types",
                "depends_on" : "" ,
                "mandatory_depends_on" : "eval: doc.customer_type == 'Company' "
            },
        ],
        "Address" : [
            {
                "fieldname": "country_subentity_code",
                "label" : "Country Subentity Code" ,
                "fieldtype" : "Link" ,
                "insert_after": "city",
                "options" : "Country Subentity Code"
            },
        ],
        "Item Tax Template" : [
            {
                "fieldname": "tax_category",
                "label" : "Tax Category" ,
                "fieldtype" : "Link" ,
                "options" : "Tax Category" ,
                "insert_after": "company",
                "reqd" : 1
            }
        ],
        "Sales Invoice" : [
            {
                "fieldname" : "uuid",
                "label" : "UUID" ,
                "fieldtype" : "Data",
                "insert_after" : "company" ,
                "no_copy" : 1,
                "read_only" : 1,
            },
            {
                "fieldname": "uploaded_to_jofotara",
                "label" : "Uploaded To Jofotara" ,
                "fieldtype" : "Check" ,
                "insert_after": "is_discounted",
                "no_copy" : 1,
                "hidden" : 1,
            },
            {
                "fieldname": "jofotara_status",
                "label" : "JoFotara Status" ,
                "fieldtype" : "Data" ,
                "insert_after": "due_date",
                "no_copy" : 1,
                "read_only" : 1
            },
            {
                "fieldname" : "reason_for_return",
                "label" : "Reasons for Return" ,
                "fieldtype" : "Data" ,
                "insert_after": "return_against",
                "no_copy" : 1,
                "depends_on" : "eval: doc.is_return",
                "mandatory_depends_on" : "eval: doc.is_return",
                "default" : "Return Invoice",
            },
            {
                "fieldname" : "jofotara_qrcode",
                "label" : "Jofotara QR" ,
                "fieldtype" : 'Attach Image' ,
                "read_only" : 1,
                "hidden" : 1 ,
                "no_copy" : 1,
                "insert_after" : "remarks",
            },
            {
                "fieldname": "update_fotara_calculation",
                "label" : "Update Fotara Calculation" ,
                "fieldtype" : "Check" ,
                "insert_after": "update_stock",
                "no_copy" : 1,
                "depends_on" : "eval: frappe.user.has_role('Administrator') == true",
                "allow_on_submit" : 1,
            },
        ],
        "Sales Taxes and Charges" : [
            {
                "fieldname": "account_type",
                "label" : "Account Type" ,
                "fieldtype" : "Data" ,
                "insert_after": "account_head",
                "read_only" : 1 ,
                "fetch_from" : "account_head.account_type",
            },
        ],
        "Sales Invoice Item" : SellingFields ,
        "POS Invoice Item" : SellingFields ,
        "Purchase Invoice Item" : SellingFields ,
        "Sales Order Item" : SellingFields ,
        "Delivery Note Item" : SellingFields,
        "Quotation Item" : SellingFields ,
		'Purchase Order Item': SellingFields,
		'Purchase Receipt Item': SellingFields,
        'Supplier Quotation Item' : SellingFields ,

        "Sales Invoice Payment" : [
            {
                "fieldname" : "payment_code" ,
                "label" : "Payment Code" ,
                "fieldtype" : "Data" ,
                "insert_after" : "type" , 
                "fetch_from" : "mode_of_payment.payment_code" ,
                "fetch_if_empty" : 1 ,
                "read_only" : 1 ,
                "no_copy" : 1 ,
            }   
        ] ,
        "Company" : [
            {
                "fieldname" : "company_name_in_arabic" ,
                "fieldtype" : "Data" ,
                "label" : "Company Name In Arabic" ,
                "insert_after" : "company_name" ,
            }
        ]
    } 

    create_custom_fields(custom_fields ,update=True)