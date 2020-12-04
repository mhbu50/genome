import frappe

def unlink_lab_test(doc, method):
    """
    On Cancel/Trash removes the Invoice reference from the Lab Test and set invoiced and paid to zero
    """
    if doc.patient:
        lab_test = frappe.get_list("Lab Test", 
        filters = {"sales_invoice": doc.name})
        if len(lab_test)> 0:
            lab_test = frappe.get_doc("Lab Test", lab_test[0].name)
            if lab_test.docstatus == 1 and lab_test.stage == 'Signed Off':
                frappe.throw(
                    "Cannot Cancel as Lab Test {} is Signed Off".format(lab_test.name))
            else:
                frappe.db.set_value("Lab Test", lab_test.name, "sales_invoice", None)
                frappe.db.set_value("Lab Test", lab_test.name, "paid", 0)
                frappe.db.set_value("Lab Test", lab_test.name, "invoiced", 0)
                frappe.db.commit()
                frappe.msgprint('Lab Test {} unlinked'.format(lab_test.name))

def before_submit(doc, method):
    verify_lab_test_status(doc)

def on_submit(doc, method):
    """
    Mark corresponding Lab Test as Invoiced
    """
    lab_test = get_lab_test_doc(doc.name)
    if lab_test:
        lab_test.db_set('invoiced', 1)

def verify_lab_test_status(doc):
    """
    Verify if the corresponding Lab Test is not in cancelled state
    """
    lab_test = get_lab_test_doc(doc.name)
    if lab_test and lab_test.docstatus == 2:
        frappe.throw(
            'Cannot Submit Sales Invoice as Lab Test {} is cancelled'.format(lab_test.name))        

def get_lab_test_doc(sales_invoice):
    lab_test_list = frappe.get_list('Lab Test', 
    filters = {
        'sales_invoice' : sales_invoice 
    })
    if lab_test_list:
        lab_test = lab_test_list[0].name
        lab_test = frappe.get_doc('Lab Test', lab_test)
        return lab_test
        