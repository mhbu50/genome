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
from frappe.utils.file_manager import delete_file, get_file, get_files_path
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

def after_insert_patient(doc, method):
    doc.hash_id = frappe.generate_hash(length=12)    
    doc.save()

@frappe.whitelist()
def add_pdf(doc):
    execute(doc)

def execute(doc):  
    envelop_name = frappe.generate_hash(length=34)
    shareable_file_name = frappe.generate_hash(length=34) 
    lab_test_doc = frappe.get_doc("Lab Test",doc) 
    lab_test_doc.envelope_id = envelop_name
    lab_test_doc.save()

    upload_dropbox(lab_test_doc.lab_test_result_file[7:])
    upload_dropbox(lab_test_doc.arabic_result_file[7:])

    sms_message = frappe.db.get_single_value('Healthcare Settings','sms_printed')
    # envelope_template = frappe.db.get_single_value('Healthcare Settings','envelope_template')

    html_data1 = frappe.render_template("templates/envlop.html",
			{"patient_name":lab_test_doc.patient_name,"disease":lab_test_doc.disease,"file1":lab_test_doc.lab_test_result_file[7:],"file2":lab_test_doc.arabic_result_file[7:],
            "shareable_file_name": shareable_file_name, "hash_id": lab_test_doc.hash_id})   
    save_and_attach(html_data1, envelop_name)
    
    disease_doc = frappe.get_doc("Diseases",lab_test_doc.disease)  
    html_data2 = frappe.render_template("templates/shareable_file1.html",
			{"disease": disease_doc.name,
             "disease_story": disease_doc.description,
             "html_pattern": disease_doc.html_pattern,
             "hash_id": lab_test_doc.hash_id})
    
    save_and_attach(html_data2, shareable_file_name)
    dbx = dropbox.Dropbox('3BJH_abhbXwAAAAAAAAeyh1LxMm9JRn2FN6TmcaWKxeVJnOJNzLJpiYGShEUKr3M')
    # print dbx.files_get_metadata('/Apps/KISSr/mhbu50.kissr.com/{}'.format(lab_test_doc.lab_test_result_file[7:]))
    # print dbx.files_get_metadata('/Apps/KISSr/mhbu50.kissr.com/{}'.format(lab_test_doc.arabic_result_file[7:]))
    print("envelop_name = {}".format(envelop_name))
    print("shareable_file_name = {}".format(shareable_file_name))
    time.sleep(5)
    check_file(lab_test_doc.lab_test_result_file[7:])
    check_file(lab_test_doc.arabic_result_file[7:])
    check_file("{}.html".format(envelop_name))
    check_file("{}.html".format(shareable_file_name))
    return "uploaded"
    # send_sms(["996504913826"], sms_message)

def get_html_data(doctype, name):
    """Document -> HTML."""
    html = frappe.get_print(doctype, name)
    return html

def save_and_attach(content, to_name):
    from frappe.utils.file_manager import save_file_on_filesystem
    file_name = "{}.html".format(to_name.replace(" ", "-").replace("/", "-")) 
    print " to_name = {} ".format(to_name)   
    save_file_on_filesystem(file_name, content, None, is_private=0)  
    upload_dropbox("{}".format(file_name),True)  

def upload_dropbox(file_name,for_delete=False):
    dbx = dropbox.Dropbox('3BJH_abhbXwAAAAAAAAeyh1LxMm9JRn2FN6TmcaWKxeVJnOJNzLJpiYGShEUKr3M')
    LOCALFILE = '{}/{}'.format(frappe.get_site_path("public", "files"),file_name) #local path 
    BACKUPPATH = '/Apps/KISSr/mhbu50.kissr.com/{}'.format(file_name) 

    with open(LOCALFILE, 'rb') as f:
            print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
            try:
                dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
                if for_delete == True:
                    print("\n\n\n in for_delete")
                    delete_file(LOCALFILE)
                for entry in dbx.files_list_folder('/Apps/KISSr/mhbu50.kissr.com').entries:
                    print(entry.name)
            except ApiError as err:
                if err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()

def check_file(file_name):
    try:
        dbx = dropbox.Dropbox('3BJH_abhbXwAAAAAAAAeyh1LxMm9JRn2FN6TmcaWKxeVJnOJNzLJpiYGShEUKr3M')
        print dbx.files_get_metadata('/Apps/KISSr/mhbu50.kissr.com/{}'.format(file_name))
    except ApiError as err:
                if err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()
