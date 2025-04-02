// Copyright (c) 2025, Basel Waheed and contributors
// For license information, please see license.txt


frappe.ui.form.on("JoFotara Logs", {
    refresh(frm) {
        frm.disable_form();
    },

    download_request_xml(frm) {
        if (frm.doc.xml_content) {
            DownloadXML(frm.doc.xml_content , "Request_" + frm.doc.reference_name) ;
        }
    },

    download_response_xml(frm) {
        if (frm.doc.response_xml && frm.doc.status == "Success") {
            DownloadXML(frm.doc.response_xml , "Response_" + frm.doc.reference_name) ;
        }
    },

});


let DownloadXML = (xml_content , file_name ) => {
    // Create a Blob object with the XML data
    const blob = new Blob([xml_content], { type: 'application/xml' });

    // Create a link element
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = file_name+ '.xml'; // Set the file name with .xml extension

    // Append the link to the body (required for Firefox)
    document.body.appendChild(link);

    // Trigger the download
    link.click();

    // Remove the link from the document
    document.body.removeChild(link);
}