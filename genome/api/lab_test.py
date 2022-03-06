import frappe
import io


@frappe.whitelist(allow_guest=True)
def download_lab_result_file(token):
    """
    prompts to downloads Lab Test File for the given token

    example:
    SITEURL/api/method/genome.api.lab_test.download_lab_result_file?token=urmDSaVqgTYwmQmz
    """
    token_doc = get_token_doc(token)

    file_path = frappe.get_all(
        'Lab Test',
        fields=['lab_result_file'],
        filters={'docstatus': ['!=', 2], 'name': token_doc[0].docname})
    site_path = frappe.get_site_path()
    if 'private' in file_path[0].lab_result_file:
        file_path = site_path + file_path[0].lab_result_file
    else:
        file_path = site_path + '/public' + file_path[0].lab_result_file
    # file_path = requote_uri(file_path)
    lab_test_file = io.open(file_path, 'rb', buffering=0)
    data = lab_test_file.read()
    if not data:
        frappe.msgprint('No data')

    frappe.local.response.filecontent = data
    frappe.local.response.type = "download"
    frappe.local.response.filename = '{}.pdf'.format(token_doc[0].docname)


@frappe.whitelist(allow_guest=True)
def update_payment_status(token, payment):
    """
    Updates payment remarks for the Lab Test

    example:
    SITEURL/api/method/genome.api.lab_test.update_payment_status?token=urmDSaVqgTYwmQmz?payment=Partially%20Paid
    """
    token_doc = get_token_doc(token)
    frappe.session.user = "Administrator"
    lab_test = frappe.get_doc('Lab Test', token_doc[0].name)
    if payment == 'Partially Paid':
        lab_test.db_set('payment_remarks', payment)
    elif payment == 'Paid':
        lab_test.db_set('payment_remarks', payment)

    frappe.session.user = "Guest"

    return payment


def get_token_doc(token):
    return frappe.get_all(
        'SMS Token',
        fields=['docname'],
        filters={'docstatus': 1, 'document_type': 'Lab Test', 'name': token})


@frappe.whitelist()
def set_access_token(name, token):
    frappe.db.set_value('Lab Test', name, 'access_token', token)


@frappe.whitelist()
def get_patient_mobile_numbers(patient):
    numbers = ""
    patient_number, customer = frappe.db.get_value("Patient", patient, ["mobile", "customer"])
    customer_number = frappe.db.get_value("Customer", customer, "mobile_no")

    if patient_number:
        numbers += str(patient_number)
    if customer_number:
        numbers += "\n{}".format(str(customer_number))
    return numbers


@frappe.whitelist()
def update_lab_result_file_link(docname):
    lab_result_file_url = frappe.db.get_value(
        'File',
        {'attached_to_doctype': 'Lab Test', 'attached_to_name': docname, 'attached_to_field': 'lab_result_file'},
        ['file_url'])

    lab_test = frappe.get_doc('Lab Test', docname)

    if lab_result_file_url:
        lab_test.db_set('lab_result_file', lab_result_file_url, update_modified=False)
    else:
        lab_test.db_set('lab_result_file', None, update_modified=False)

    lab_test.notify_update()
