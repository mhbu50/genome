import frappe

def unlink_lab_test(doc, method):
    if doc.patient:
        lab_test = frappe.get_list("Lab Test", 
        filters = {"sales_invioce": doc.name})
        if len(lab_test)> 0:
            lab_test = frappe.get_doc("Lab Test", lab_test[0].name)
            if lab_test.docstatus == 1:
                frappe.throw("Cannot Cancel as Linked Lab Test is submitted")
            else:
                frappe.db.set_value("Lab Test", lab_test.name, "sales_invoice", None)