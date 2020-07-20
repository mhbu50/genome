# -*- coding: utf-8 -*-
# Copyright (c) 2020, Accurate Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabTestFinding(Document):
	def validate(self):
		share = False
		for row in self.diseases:
			if row.share: share = True
		if share: self.share = 1
		else: self.share = 0