import frappe

@frappe.whitelist()
def set_access_token(name, token):
    frappe.db.set_value('Sales Invoice', name, 'access_token', token)