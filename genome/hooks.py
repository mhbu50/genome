# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "genome"
app_title = "Genome"
app_publisher = "Accurate Systems"
app_description = "genome"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@accuratesystems.com.sa"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/css/genome.css"
app_include_js = "/assets/js/genome.js"

# include js, css files in header of web template
# web_include_css = "/assets/genome/css/genome.css"
# web_include_js = "/assets/genome/js/genome.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Patient" : "public/js/patient.js","Lab Test":"public/js/lab_test.js"}
# doctype_list_js = {"Lab Test" : "public/js/lab_test_finding_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "genome.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "genome.install.before_install"
# after_install = "genome.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "genome.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Patient": {
		"after_insert": "genome.genome.tool.after_insert_patient"
	},
	"Lab Test": {"validate": "genome.utils.lab_test.generate_sales_invoice"},
	"Sales Invoice": {
        "cancel": "genome.utils.sales_invoice.unlink_lab_test",
        "trash": "genome.utils.sales_invoice.unlink_lab_test",
		"before_submit": "genome.utils.sales_invoice.before_submit",
		"on_submit": "genome.utils.sales_invoice.on_submit"
    },
	"Payment Entry": {
		'on_submit': "genome.utils.payment_entry.on_submit",
		"cancel": "genome.utils.payment_entry.cancel"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"genome.tasks.all"
# 	],
# 	"daily": [
# 		"genome.tasks.daily"
# 	],
# 	"hourly": [
# 		"genome.tasks.hourly"
# 	],
# 	"weekly": [
# 		"genome.tasks.weekly"
# 	]
# 	"monthly": [
# 		"genome.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "genome.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "genome.event.get_events"
# }

fixtures = [
	{
		'dt': 'Workflow',
		'filters': [
			['name', 'in', [
				'Lab Test'
			]]
		]
	},
	{
                'dt': 'Workflow State',
                'filters': [
                        ['name', 'in', [
                                'Draft',
				'Sample Scheduled',
				'Consent Provided',
				'Sample Deposited',
				'Sample Shipped',
				'Result Received',
				'Envelope Sent',
				'Signed Off'
                        ]]
                ]
        }

]

# Monkey Patches
from genome.monkey_patching import patient