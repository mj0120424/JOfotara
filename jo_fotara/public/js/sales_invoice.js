frappe.ui.form.on("Sales Invoice" , {
    refresh(frm) {
        frm.trigger("add_jofotara_button");
    },

    add_jofotara_button(frm) {

        let AllowedCompany = frappe.boot.jofotara_settings ;

        if (frm.doc.docstatus == 1 && frm.doc.uploaded_to_jofotara == 0 && AllowedCompany.includes(frm.doc.company)) {
            frm.add_custom_button(__("Resend To Jofotara") , () => {
                frappe.call({
                    method: "jo_fotara.fotara.invoice.resend_invoice",
                    args:{
                        invoice_name: frm.doc.name,
                    },
                    freeze: true,
                    freeze_message: __("Resending Invoice ..."),
                    callback:(r)=>{
                        cur_frm.reload_doc();
                    }
                })
            })      
        }
    }

})