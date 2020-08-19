import frappe


def on_submit(doc, method):
    update_lab_test(doc)

def cancel(doc, method):
    update_lab_test_on_cancel(doc)


def update_lab_test(doc):
    """
    Will mark Lab Test as paid if it exists for the Paid Sales Invoice 
    """
    for row in doc.references:
        if row.reference_doctype == 'Sales Invoice':
            status = frappe.db.get_value(
                'Sales Invoice', row.reference_name, 'status')
            if status == 'Paid':
                from genome.utils.sales_invoice import get_lab_test_doc
                lab_test = get_lab_test_doc(row.reference_name)
                if lab_test:
                    lab_test.db_set('paid', 1)

def update_lab_test_on_cancel(doc):
    """
    Will mark Lab Test as unpaid if it exists for the related Sales Invoice 
    """
    for row in doc.references:
        if row.reference_doctype == 'Sales Invoice':
            status = frappe.db.get_value(
                'Sales Invoice', row.reference_name, 'status')
            if status != 'Paid':
                from genome.utils.sales_invoice import get_lab_test_doc
                lab_test = get_lab_test_doc(row.reference_name)
                if lab_test:
                    lab_test.db_set('paid', 0)