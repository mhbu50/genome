from __future__ import unicode_literals
import frappe
import json
import sys
import time
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, getdate, add_years, time_diff, get_datetime_str
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils.pdf import get_pdf
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils.file_manager import delete_file
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

def after_insert_patient(doc, method):
    doc.hash_id = frappe.generate_hash(length=12)    
    doc.save()

@frappe.whitelist()
def add_pdf(doc,disease):
    execute(doc,disease)
    frappe.enqueue(method=execute, queue='long', timeout=30, is_async=True,
            **{"doc": doc,"disease": disease})

def execute(doc,disease):  
    envelop_name = frappe.generate_hash(length=36)
    shareable_file_name = frappe.generate_hash(length=36) 
    lab_test_doc = frappe.get_doc("Lab Test",doc) 
    upload_dropbox(lab_test_doc.lab_test_result_file[7:])
    upload_dropbox(lab_test_doc.arabic_result_file[7:])

    sms_message = frappe.db.get_single_value('Healthcare Settings','sms_printed')
    envelope_template = frappe.db.get_single_value('Healthcare Settings','envelope_template')

    html_data1 = frappe.render_template("templates/envelop.html",
			{"envelope_template":envelope_template,"file1":lab_test_doc.lab_test_result_file[7:],"file2":lab_test_doc.arabic_result_file[7:],
            "shareable_file_name": shareable_file_name, "hashid": 46546546546})   
    save_and_attach(html_data1, envelop_name)
    
    disease_doc = frappe.get_doc("Diseases",disease)  
    html_data2 = frappe.render_template("templates/shareable_file.html",
			{"disease": disease_doc.name,
             "disease_story": disease_doc.description,
             "html_pattern": disease_doc.html_pattern})
    
    save_and_attach(html_data2, shareable_file_name)
    send_sms(["996504913826"], sms_message)

def get_html_data(doctype, name):
    """Document -> HTML."""
    html = frappe.get_print(doctype, name)
    return html

def save_and_attach(content, to_name):
    from frappe.utils.file_manager import save_file_on_filesystem
    file_name = "{}.html".format(to_name.replace(" ", "-").replace("/", "-")) 
    print " to_name = {} ".format(to_name)   
    save_file_on_filesystem(file_name, content, None, is_private=0)  
    upload_dropbox("{}".format(file_name))  

def upload_dropbox(file_name):
    dbx = dropbox.Dropbox('3BJH_abhbXwAAAAAAAAeyh1LxMm9JRn2FN6TmcaWKxeVJnOJNzLJpiYGShEUKr3M')

    LOCALFILE = '/home/mohd/new-bench/sites/genome.org/public/files/{}'.format(file_name) #local path 
    BACKUPPATH = '/Apps/KISSr/mhbu50.kissr.com/{}'.format(file_name) 

    with open(LOCALFILE, 'rb') as f:
            print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
            try:
                dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
                for entry in dbx.files_list_folder('/Apps/KISSr/mhbu50.kissr.com').entries:
                    print(entry.name)
                # time.sleep(2)
                # shared_link_metadata = dbx.sharing_create_shared_link_with_settings(BACKUPPATH)
                # print (shared_link_metadata.url)


		        # delete_file(existing_file)

            except ApiError as err:
                if err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()