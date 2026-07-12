# Copyright (c) 2026, Laida L and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class StorageOnboardingCase(Document):
    def validate(self):
        # set sales officer = creator, only once
        if not self.sales_officer:
            self.sales_officer = self.owner

        # compute amount per row + total
        total = 0
        for row in self.requested_packages:
            if row.qty is None or row.qty < 0:
                frappe.throw("Quantity cannot be negative")
            if row.rate is None or row.rate < 0:
                frappe.throw("Rate cannot be negative")
            discount = row.discount_percent or 0
            row.amount = (row.qty or 0) * (row.rate or 0) * (1 - discount / 100.0)
            total += row.amount
        self.total_amount = total
