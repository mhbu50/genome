import frappe

def generate_sales_invoice(doc, method):
    '''
    On creation of new Lab test generates Sales invoice 
    using the item from the template field and link it with the lab test.
    '''
    if doc.sales_invoice: return
    item_code, lab_test_rate = frappe.get_value('Lab Test Template', doc.template, ['item', 'lab_test_rate'])
    sales_invoice = frappe.new_doc("Sales Invoice")
    sales_invoice.patient = doc.patient
    sales_invoice.patient_name = doc.patient_name
    sales_invoice.ref_practitioner = doc.practitioner
    sales_invoice.customer_name_in_arabic = doc.arabic_first_name
    sales_invoice.customer = frappe.get_value('Patient', doc.patient, "customer")
    sales_invoice.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": lab_test_rate
    })
    sales_invoice.save()
    doc.sales_invoice = sales_invoice.name

@frappe.whitelist()
def get_lab_test_finding_count(patient, labtest):
    return frappe.db.count('Lab Test Finding', {'patient': patient, 'lab_test_id': labtest})