import frappe
from erpnext.healthcare.doctype.patient.patient import Patient

class CustomPatient(Patient):

    def create_website_user(self):
        """
        Create a website user for the patient depending upon the settings
        """
        add_patient_as_a_website_user = frappe.db.get_single_value ('Genome Settings', 'add_patient_as_a_website_user')
        if add_patient_as_a_website_user:
            super().create_website_user()
