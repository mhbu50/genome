import frappe
import io

@frappe.whitelist(allow_guest=True)
def download_lab_result_file(token):
    """
    prompts to downloads Lab Test File for the given token
    
    example:
    SITEURL/api/method/genome.api.lab_test.download_lab_result_file?token=urmDSaVqgTYwmQmz
    """
    token_doc = frappe.get_all('SMS Token', fields= ['docname'], 
    filters = {'docstatus': 1, 'document_type': 'Lab Test', 'name': token})

    file_path = frappe.get_all('Lab Test', fields= ['lab_result_file'],
    filters = {'docstatus': ['!=', -1], 'name': token_doc[0].docname})
    site_path = frappe.get_site_path()
    file_path = site_path + file_path[0].lab_result_file
    lab_test_file = io.open(file_path, 'rb', buffering=0)
    data = lab_test_file.read()
    if not data:
        frappe.msgprint('No data')
    
    frappe.local.response.filecontent = data
    frappe.local.response.type = "download"
    frappe.local.response.filename = f'{token_doc[0].docname}.pdf'