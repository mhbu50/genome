# encoding=utf8
from __future__ import unicode_literals
import frappe
import os
# import dropbox
import json
import time
from ftplib import FTP
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, getdate, add_years, time_diff, get_datetime_str
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import delete_file, get_file, get_files_path

def after_insert_patient(doc, method):
    doc.hash_id = frappe.generate_hash(length=12)
    doc.save()


@frappe.whitelist()
def add_pdf(doc):
    envlop_file_name = frappe.generate_hash(length=12)
    shareable_file_name = frappe.generate_hash(length=12)
    lab_test_doc = frappe.get_doc("Lab Test", doc)

    ftp = FTP('ftp.saudigenome.net')
    ftp.login(user='envelope@saudigenome.net', passwd = '216408Mm')
    print (ftp.getwelcome())
    #upload test_result
    filename = get_file_path(
        lab_test_doc.lab_test_result_file[7:])
    print ("\nfilename 1= {} \n ".format(filename))
    file = open(filename, 'rb')
    ftp.storbinary('STOR '+lab_test_doc.lab_test_result_file[7:].encode('utf-8').decode('utf-8'), file)
    file.close()
    #upload arabic_result
    filename = get_file_path(
        lab_test_doc.arabic_result_file[7:])
    print ("\nfilename 2= {} \n ".format(filename))
    file = open(filename, 'rb')
    ftp.storbinary('STOR '+lab_test_doc.arabic_result_file[7:].encode('utf-8').decode('utf-8'), file)
    file.close()
    #upload envlop_file
    html_data1 = frappe.render_template("templates/envlop.html",
                                        {"patient_name": lab_test_doc.arabic_first_name, "disease": lab_test_doc.disease_description, "file1": lab_test_doc.lab_test_result_file[7:], "file2": lab_test_doc.arabic_result_file[7:],
                                        "shareable_file_name": shareable_file_name, "hash_id": lab_test_doc.hash_id})
    envlop_file = save_generated_file(html_data1, envlop_file_name)
    filename = get_file_path(envlop_file)
    print ("\n envlop_file = {} filename 3= {} \n ".format(envlop_file,filename))
    file = open(filename, 'rb')
    ftp.storbinary('STOR '+envlop_file, file)
    file.close()
    # upload shareable_file
    disease_doc = frappe.get_doc("Diseases", lab_test_doc.disease)
    html_data2 = frappe.render_template("templates/shareable_file.html",
                                        {"disease": disease_doc.name,
                                        "disease_story": disease_doc.description,
                                        "html_pattern": disease_doc.html_pattern,
                                        "hash_id": lab_test_doc.hash_id})
    shareable_file = save_generated_file(html_data2, shareable_file_name)
    filename = get_file_path(shareable_file)
    print ("\n shareable_file = {} filename 4= {} \n ".format(envlop_file,filename))
    file = open(filename, 'rb')
    ftp.storbinary('STOR '+shareable_file, file)
    file.close()
    ftp.quit()
    print ("\nuploaded \n")
    return envlop_file_name


def get_html_data(doctype, name):
    """Document -> HTML."""
    html = frappe.get_print(doctype, name)
    return html


def save_generated_file(content, to_name):
    from frappe.utils.file_manager import save_file_on_filesystem
    file_name = "{}.html".format(to_name.replace(" ", "-").replace("/", "-"))
    save_file_on_filesystem(file_name, content, None, is_private=0)
    return file_name


def get_file_path(file_name):
    return '{}/{}'.format(frappe.get_site_path("public", "files"), file_name)
