import frappe
import json

def validate_file_attachment(doc, method):
    if doc.lab_result_file:
        file_list = frappe.get_list('File', {
            'attached_to_doctype': doc.doctype,
            'attached_to_name': doc.name,
            'file_url': doc.lab_result_file
        }, ['name', 'is_private'])
        if not file_list[0].is_private:
            doc.lab_result_file = None
            frappe.delete_doc('File', file_list[0].name)
            frappe.msgprint('Please attach files as Private.')
        else:
            frappe.msgprint('File Attached Successfully')


def generate_sales_invoice(doc, method):
    '''
    On creation of new Lab test generates Sales invoice 
    using the item from the template field and link it with the lab test.
    '''
    if doc.sales_invoice: return
    item_code, lab_test_rate = frappe.get_value('Lab Test Template', doc.template, ['item', 'lab_test_rate'])
    sales_invoice = frappe.new_doc("Sales Invoice")
    doc_map = {
        'patient' : 'patient',
        'patient_name': 'patient_name',
        'ref_practitioner': 'practitioner',
        'customer_name_in_arabic': 'arabic_first_name',
        'national_id': 'national_id'
    }
    for key, value in doc_map.items():
        setattr(sales_invoice, key, 
        getattr(doc, value))
    
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

@frappe.whitelist()
def set_introduction_conclusion(docname ,introduction = None, conclusion = None):
    '''
    Set introduction and conclusion after submit in Lab test
    '''
    doc = frappe.get_doc('Lab Test', docname)
    doc.db_set('result_introduction', introduction)
    doc.db_set('result_conclusion', conclusion)
    frappe.db.commit()

@frappe.whitelist()
def set_courier_details(values, lab_test_id):
    values = json.loads(values)
    if 'courier' in values or 'air_way_bill_no'  in values:
        ct_doc = frappe.new_doc('Courier Tracking')
        ct_doc.courier = values['courier']
        ct_doc.air_way_bill_no = values['air_way_bill_no']
        ct_doc.insert()
        ct_doc.submit()
        update_cd_in_lab_test(
            lab_test_id, ct_doc.name, ct_doc.courier, ct_doc.air_way_bill_no
        )
    elif 'courier' in values or 'air_way_bill_no'  in values:
        frappe.throw('Please enter both Courier and Air Way Bill#')
    elif 'courier_note' in values:
        ct_doc = frappe.get_doc('Courier Tracking', values['courier_note'])
        update_cd_in_lab_test(
            lab_test_id, ct_doc.name, ct_doc.courier, ct_doc.air_way_bill_no
        )
    else:
        frappe.throw('Please enter the information')
    
def update_cd_in_lab_test(lab_test_id, name, courier, air_way_bill_no):
    frappe.db.set_value('Lab Test', lab_test_id, 'courier_note', name)
    frappe.db.set_value('Lab Test', lab_test_id, 'courier', courier)
    frappe.db.set_value('Lab Test', lab_test_id, 'air_way_bill_no', air_way_bill_no)
