from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, getdate, add_years, time_diff, get_datetime_str
from frappe.model.document import Document
from datetime import datetime, timedelta
from six import iteritems

def after_insert_patient(doc, method):
    doc.hash_id = frappe.generate_hash(length=7)
    doc.save()