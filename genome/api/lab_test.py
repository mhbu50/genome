import frappe
import io
from requests.utils import requote_uri

@frappe.whitelist(allow_guest=True)
def download_lab_result_file(token):
    """
    prompts to downloads Lab Test File for the given token
    
    example:
    SITEURL/api/method/genome.api.lab_test.download_lab_result_file?token=urmDSaVqgTYwmQmz
    """
    token_doc = get_token_doc(token)

    file_path = frappe.get_all('Lab Test', fields= ['lab_result_file'],
    filters = {'docstatus': ['!=', 2], 'name': token_doc[0].docname})
    site_path = frappe.get_site_path()
    if 'private' in file_path[0].lab_result_file:
        file_path = site_path + file_path[0].lab_result_file
    else:
        file_path = site_path + '/public' + file_path[0].lab_result_file
    file_path = requote_uri(file_path)
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
    return frappe.get_all('SMS Token', fields= ['docname'], 
    filters = {'docstatus': 1, 'document_type': 'Lab Test', 'name': token})

@frappe.whitelist()
def set_access_token(name, token):
    frappe.db.set_value('Lab Test', name, 'access_token', token)