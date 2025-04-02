import frappe
from lxml import etree
from frappe.utils import flt

NameSpace = {
    "cac" : "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc" : "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext" : "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2" ,
}



class FotaraXML :
    def __init__(self , jofotara_invoice:dict={}):
        
        self.jofotara_invoice = jofotara_invoice
        self.currency_symbol = self.jofotara_invoice.get("CurrencySybmol")
        self.handle_xml_data()
      
        
    def handle_xml_data(self) :
        
        self.create_xml()
        
        self.add_general_data()
        self.add_company_data()
        self.add_customer_data()
        self.add_seller_supplier_party()
        self.add_payment_means()
        self.add_discounts()
        self.add_taxes()
        self.add_totals_data()
        self.add_invoice_lines()
        


    def create_xml(self) :
        path_of_tree = frappe.get_app_path("jo_fotara" , "fotara" , "data" , "structure.xml")
        tree  = etree.parse(path_of_tree)
        self.root = tree.getroot()
        
        
    def add_general_data(self) :
        
        ProfileID = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ProfileID")
        ProfileID.text = self.jofotara_invoice.get("ProfileID")
        
        InvoiceID = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        InvoiceID.text = self.jofotara_invoice.get("Invoice-ID")
        
        UUID = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UUID")
        UUID.text = self.jofotara_invoice.get("Invoice-UUID")
        self.uuid = self.jofotara_invoice.get("Invoice-UUID")
        
        IssueDate = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate")
        IssueDate.text = self.jofotara_invoice.get("IssueDate")
        

        InvoiceTypeCode = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode")
        InvoiceTypeCode.text = self.jofotara_invoice.get("InvoiceTypeCode")
        InvoiceTypeCode.set("name" , self.jofotara_invoice.get("InvoiceTypeCode-name"))
        
        Note = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Note")
        Note.text = self.jofotara_invoice.get("Note")
        
        DocumentCurrencyCode = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentCurrencyCode")
        DocumentCurrencyCode.text = self.jofotara_invoice.get("DocumentCurrencyCode")
        
        TaxCurrencyCode = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxCurrencyCode")
        TaxCurrencyCode.text = self.jofotara_invoice.get("TaxCurrencyCode")

        if self.jofotara_invoice.get("InvoiceTypeCode") in ["381"]  :
            BillingReference = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}BillingReference")
            InvoiceDocumentReference = etree.SubElement(BillingReference ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceDocumentReference")
            InvoiceDocumentReferenceID = etree.SubElement(InvoiceDocumentReference , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            InvoiceDocumentReferenceID.text = self.jofotara_invoice.get("InvoiceDocumentReference-ID")
            
            BillingReferenceUUID = etree.SubElement(InvoiceDocumentReference ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UUID")
            BillingReferenceUUID.text = self.jofotara_invoice.get("BillingReference-UUID")
            
            DocumentDescription = etree.SubElement(InvoiceDocumentReference , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentDescription")
            DocumentDescription.text = self.jofotara_invoice.get("DocumentDescription")
            
            BillingReference.tail ="\n    "
            etree.indent(BillingReference , space="    " , level=1)
            TaxCurrencyCode.addnext(BillingReference)
        
        ICV = self.root.find('.//cac:AdditionalDocumentReference[cbc:ID="ICV"]/cbc:UUID', NameSpace)
        ICV.text = self.jofotara_invoice.get("ICV")
        
        
        
    def add_company_data(self) :
        
        company : dict = self.jofotara_invoice.get("company")
        
        CompanyID = self.root.find(".//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID" , NameSpace)
        CompanyID.text = company.get("CompanyID")
        
        RegistrationName = self.root.find(".//cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName" , NameSpace)
        RegistrationName.text = company.get("RegistrationName")
         
        
    def add_customer_data(self) :
        
        customer : dict = self.jofotara_invoice.get("customer")
        
        AccountingCustomerParty  = self.root.find(".//cac:AccountingCustomerParty" , NameSpace)
        Party= etree.SubElement(AccountingCustomerParty , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party")
        
        if customer.get("PartyIdentification-ID") and customer.get("PartyIdentification-schemeID") :
        
            PartyIdentification = etree.SubElement(Party , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification")
            PartyIdentificationID = etree.SubElement(PartyIdentification , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            PartyIdentificationID.text = customer.get("PartyIdentification-ID")
            PartyIdentificationID.set("schemeID" , customer.get("PartyIdentification-schemeID"))


        PostalAddress = etree.SubElement(Party , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PostalAddress")

        if postal_zone := customer.get("PostalZone") :
            PostalZone = etree.SubElement(PostalAddress , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PostalZone")
            PostalZone.text = postal_zone
            
        if country_subentity_code := customer.get("CountrySubentityCode") :
            CountrySubentityCode = etree.SubElement(PostalAddress , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CountrySubentityCode")
            CountrySubentityCode.text = country_subentity_code
                

        Country = etree.SubElement(PostalAddress , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Country")
        IdentificationCode = etree.SubElement(Country , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IdentificationCode")
        IdentificationCode.text = customer.get("IdentificationCode")


        PartyTaxScheme = etree.SubElement(Party , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyTaxScheme")
        
        if company_id := customer.get("CompanyID") :
            CompanyID = etree.SubElement(PartyTaxScheme ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CompanyID")
            CompanyID.text = company_id
            
        TaxScheme = etree.SubElement(PartyTaxScheme , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme")
        TaxSchemeID = etree.SubElement(TaxScheme , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        TaxSchemeID.text = "VAT"
            

        PartyLegalEntity = etree.SubElement(Party , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity")
        RegistrationName = etree.SubElement(PartyLegalEntity , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName")
        RegistrationName.text = customer.get("RegistrationName")
        
        if telephone := customer.get("phone") :
            
            AccountingContact = etree.SubElement(AccountingCustomerParty , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingContact")
            Telephone = etree.SubElement(AccountingContact , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Telephone")
            Telephone.text = telephone
            
        etree.indent(AccountingCustomerParty , space="    " , level=1)
    
    
    def add_seller_supplier_party(self) :
        
        company : dict = self.jofotara_invoice.get("company")
        
        PartyIdentificationID = self.root.find(".//cac:SellerSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID" , NameSpace)
        PartyIdentificationID.text = company.get("PartyIdentification-ID")
        
        
    def add_payment_means(self) :
        
        SellerSupplierParty = self.root.find(".//cac:SellerSupplierParty" , NameSpace)
        
        
        if self.jofotara_invoice.get("InvoiceTypeCode") in ["381"] :
          
            PaymentMeans = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PaymentMeans")
            PaymentMeansCode = etree.SubElement(PaymentMeans , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PaymentMeansCode")
            PaymentMeansCode.set("listID" , "UN/ECE 4461")
            PaymentMeansCode.text = self.jofotara_invoice.get("PaymentMeansCode")
            
            InstructionNote = etree.SubElement(PaymentMeans , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InstructionNote")
            InstructionNote.text = self.jofotara_invoice.get("InstructionNote")
    
            PaymentMeans.tail =  "\n    "
            etree.indent(PaymentMeans , level=1 , space="    ")
            
            SellerSupplierParty.addnext(PaymentMeans)

        

    def add_discounts(self) :
        
        if allowance_charge  := self.jofotara_invoice.get("AllowanceCharge") :
        
            BASETaxTotal = self.root.find(".//cac:TaxTotal" , NameSpace)
            DocumentCurrencyCode = self.jofotara_invoice.get("DocumentCurrencyCode")
            
            AllowanceCharge = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AllowanceCharge")
            ChargeIndicator = etree.SubElement(AllowanceCharge ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ChargeIndicator")
            ChargeIndicator.text = allowance_charge.get("ChargeIndicator")
            
            AllowanceChargeReason = etree.SubElement(AllowanceCharge , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AllowanceChargeReason")
            AllowanceChargeReason.text  = allowance_charge.get("AllowanceChargeReason")
            
            Amount = etree.SubElement(AllowanceCharge ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Amount")
            Amount.set("currencyID" , DocumentCurrencyCode )
            Amount.text = allowance_charge.get("Amount")
            
            AllowanceCharge.tail = "\n    "
            etree.indent(AllowanceCharge , space="    " , level=1) 
            
            BASETaxTotal.addprevious(AllowanceCharge)
                
            
    def add_taxes(self) :
        
        taxes : dict = self.jofotara_invoice.get("taxes")
        
        BASETaxTotal = self.root.find(".//cac:TaxTotal" , NameSpace)
        BASETaxTotal.tail = "\n    "
        BASETaxAmount = BASETaxTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
        BASETaxAmount.text = taxes.get("TaxTotal-TaxAmount-BASE")
        BASETaxAmount.set("currencyID" , self.currency_symbol)
        
        if taxes.get("TaxSubtotal") :
        
            TaxTotal = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal")
            TaxTotal.tail = "\n    "
            TaxAmount = etree.SubElement(TaxTotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
            TaxAmount.set("currencyID" , self.currency_symbol)
            TaxAmount.text = taxes.get("TaxTotal-TaxAmount")
            TaxAmount.tail = "\n"

            for tax in taxes.get("TaxSubtotal") :
                TaxSubtotal = etree.SubElement(TaxTotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal")
                TaxableAmount = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxableAmount")
                TaxableAmount.text = str(flt(tax.get("TaxableAmount"), 2))
                TaxableAmount.set("currencyID" , self.currency_symbol)
                TaxAmount = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
                TaxAmount.set("currencyID" , self.currency_symbol )
                TaxAmount.text = str(tax.get("TaxAmount"))
                
                TaxCategory = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxCategory")
                TaxCategoryID = etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
                TaxCategoryID.set("schemeID" ,"UN/ECE 5305" )
                TaxCategoryID.set("schemeAgencyID" , "6")
                TaxCategoryID.text = tax.get("TaxCategory-ID")
                
                TaxCategoryPercent = etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent")
                TaxCategoryPercent.text = tax.get("Percent")
                
                TaxScheme =etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme" )
                TaxSchemeID = etree.SubElement(TaxScheme , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
                TaxSchemeID.set("schemeID" ,"UN/ECE 5305" )
                TaxSchemeID.set("schemeAgencyID" , "6")
                TaxSchemeID.text = "VAT"


            etree.indent(TaxTotal ,space="    " , level=1) 
            BASETaxTotal.addnext(TaxTotal)
    
             
    def add_totals_data(self) :
        
        LegalMonetaryTotal = self.root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}LegalMonetaryTotal")

        TaxExclusiveAmount = LegalMonetaryTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExclusiveAmount")
        TaxExclusiveAmount.set("currencyID" , self.currency_symbol )
        TaxExclusiveAmount.text = self.jofotara_invoice.get("TaxExclusiveAmount")

        TaxInclusiveAmount = LegalMonetaryTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxInclusiveAmount")
        TaxExclusiveAmount.set("currencyID" , self.currency_symbol )
        TaxInclusiveAmount.text = self.jofotara_invoice.get("TaxInclusiveAmount")

        AllowanceTotalAmount = LegalMonetaryTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AllowanceTotalAmount")
        AllowanceTotalAmount.set("currencyID" , self.currency_symbol )
        AllowanceTotalAmount.text = self.jofotara_invoice.get("AllowanceTotalAmount")

        PrepaidAmount = LegalMonetaryTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PrepaidAmount")
        PrepaidAmount.set("currencyID" , self.currency_symbol )
        PrepaidAmount.text = self.jofotara_invoice.get("PrepaidAmount")

        PayableAmount = LegalMonetaryTotal.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PayableAmount")
        PayableAmount.set("currencyID" , self.currency_symbol)
        PayableAmount.text = self.jofotara_invoice.get("PayableAmount")
        
        
    def add_invoice_lines(self) :
        
        LegalMonetaryTotal = self.root.find(".//cac:LegalMonetaryTotal" , NameSpace)
        LegalMonetaryTotal.tail = "\n    "

        for item in reversed(self.jofotara_invoice.get("items" , [])) :
            
            InvoiceLine = etree.Element("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceLine")
            InvoiceLine.tail = "    "
            InvoiceLineID = etree.SubElement(InvoiceLine,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            InvoiceLineID.text = item.get("InvoiceLine-ID")
            
            InvoicedQuantity = etree.SubElement(InvoiceLine , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity")
            InvoicedQuantity.set("unitCode" , item.get("InvoicedQuantity-unitCode"))
            InvoicedQuantity.text = item.get("InvoicedQuantity")
            
            LineExtensionAmount = etree.SubElement(InvoiceLine , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount")
            LineExtensionAmount.set("currencyID" , self.currency_symbol)
            LineExtensionAmount.text = item.get("LineExtensionAmount")
            
            TaxTotal = etree.SubElement(InvoiceLine ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal")
            TaxAmount = etree.SubElement(TaxTotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
            TaxAmount.set("currencyID" , self.currency_symbol)
            TaxAmount.text = item.get("TaxAmount")
            RoundingAmount = etree.SubElement(TaxTotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RoundingAmount")
            RoundingAmount.set("currencyID" , self.currency_symbol)
            RoundingAmount.text = item.get("RoundingAmount")
            
            TaxSubtotal = etree.SubElement(TaxTotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal")
            TaxableAmount = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxableAmount")
            TaxableAmount.text = item.get("TaxSubtotal-TaxableAmount")
            TaxableAmount.set("currencyID" , self.currency_symbol)
            TaxAmount = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount")
            TaxAmount.set("currencyID" , self.currency_symbol )
            TaxAmount.text = item.get("TaxSubtotal-TaxAmount")
            
            TaxCategory = etree.SubElement(TaxSubtotal , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxCategory")
            TaxCategoryID = etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            TaxCategoryID.set("schemeID" ,"UN/ECE 5305" )
            TaxCategoryID.set("schemeAgencyID" , "6")
            TaxCategoryID.text = item.get("TaxCategory-ID")
            
            TaxCategoryPercent = etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent")
            TaxCategoryPercent.text = item.get("TaxCategory-Percent")
            
            TaxScheme =etree.SubElement(TaxCategory , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme" )
            TaxSchemeID = etree.SubElement(TaxScheme , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
            TaxSchemeID.set("schemeID" ,"UN/ECE 5305" )
            TaxSchemeID.set("schemeAgencyID" , "6")
            TaxSchemeID.text = "VAT"
            
            
            Item = etree.SubElement(InvoiceLine , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item")
            Name = etree.SubElement(Item , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name")
            Name.text = item.get("Name")
            
            
            Price = etree.SubElement(InvoiceLine , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price")
            PriceAmount = etree.SubElement(Price , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount")
            PriceAmount.set("currencyID" , self.currency_symbol)
            PriceAmount.text = item.get("PriceAmount")
            
            # BaseQuantity = etree.SubElement(Price ,"{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}BaseQuantity" )
            # BaseQuantity.set("unitCode" , "C62")
            # BaseQuantity.text = item.get("BaseQuantity")
            
            if item.get("AllowanceCharge-Amount") : 
            
                AllowanceCharge = etree.SubElement(Price , "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AllowanceCharge")
                ChargeIndicator = etree.SubElement(AllowanceCharge , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ChargeIndicator")
                ChargeIndicator.text = item.get("AllowanceCharge-Indicator")
                AllowanceChargeReason = etree.SubElement(AllowanceCharge , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AllowanceChargeReason")
                AllowanceChargeReason.text = item.get("AllowanceCharge-Reason")
                Amount = etree.SubElement(AllowanceCharge , "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Amount")
                Amount.set("currencyID" , self.currency_symbol)
                Amount.text = item.get("AllowanceCharge-Amount", "0.00")
            
            InvoiceLine.tail = "\n" if len(self.jofotara_invoice.get("items")) == int(item.get("InvoiceLine-ID"))  else "\n    "
            etree.indent(InvoiceLine , space="    " , level=1) 
            
            LegalMonetaryTotal.addnext(InvoiceLine)
        