import frappe

def validate_private_check(doc, method):
    '''
    on validate validates if is_private is set to 1
    '''
    if doc.attached_to_doctype in ['Lab Test', 'Lab Test Finding']:
        if doc.is_private == 0:
            pass
            # doc.delete()