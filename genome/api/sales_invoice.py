import frappe
from frappe.core.doctype.communication.email import get_attach_link
from frappe.utils import get_url
from frappe.core.utils import get_parent_doc
from requests.utils import requote_uri

@frappe.whitelist()
def set_access_token(name, token):
    frappe.db.set_value('Sales Invoice', name, 'access_token', token)


@frappe.whitelist()
def get_attachment_link(doc, print_format):
    doc = frappe.get_doc('Sales Invoice', doc)
    setattr(doc, 'reference_doctype', 'Sales Invoice')
    setattr(doc, 'reference_name', doc.name)

    key = doc.get_signature()

    # Not Supported in python 2
    # link = f'{ get_url() }/{ doc.doctype }/{ doc.name }?format={ print_format}&key={ key }'
    link = "{url}/{doctype}/{name}?format={print_format}&key={key}".format(
        url = get_url(),
        doctype = doc.doctype,
        name = doc.name,
        print_format = print_format,
        key = key
    )
    link = requote_uri(link)
    return link