import frappe

def unlink_lab_test(doc, method):
    if doc.patient:
        lab_test = frappe.get_list("Lab Test", 
        filters = {"sales_invoice": doc.name})
        if len(lab_test)> 0:
            lab_test = frappe.get_doc("Lab Test", lab_test[0].name)
            if lab_test.docstatus == 1:
                frappe.throw(f"Cannot Cancel as Lab Test {lab_test.name} is submitted")
            else:
                frappe.db.set_value("Lab Test", lab_test.name, "sales_invoice", None)

def before_submit(doc, method):
    verify_lab_test_status(doc)

def on_submit(doc, method):
    lab_test = get_lab_test_doc(doc.name)
    if lab_test:
        lab_test.db_set('invoiced', 1)

def verify_lab_test_status(doc):
    lab_test = get_lab_test_doc(doc.name)
    if lab_test and lab_test.docstatus == 2:
        frappe.throw(
            f'Cannot Submit Sales Invoice as Lab Test {lab_test.name} is cancelled')        

def get_lab_test_doc(sales_invoice):
    lab_test_list = frappe.get_list('Lab Test', 
    filters = {
        'sales_invoice' : sales_invoice 
    })
    if lab_test_list:
        lab_test = lab_test_list[0].name
        lab_test = frappe.get_doc('Lab Test', lab_test)
        return lab_test
        