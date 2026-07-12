# Copyright (c) 2026, Laida L and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe.utils import now_datetime, get_datetime


def execute(filters=None):
    columns = [
        {
            "label": "Case",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Storage Onboarding Case",
            "width": 160,
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 180,
        },
        {
            "label": "Sales Officer",
            "fieldname": "sales_officer",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": "Days Pending",
            "fieldname": "days_pending",
            "fieldtype": "Int",
            "width": 110,
        },
    ]

    cases = frappe.get_all(
        "Storage Onboarding Case",
        filters={"workflow_state": "Pending Approval"},
        fields=["name", "customer", "sales_officer", "modified"],
    )

    now = now_datetime()
    data = []
    for c in cases:
        days = (now - get_datetime(c.modified)).days
        data.append(
            {
                "name": c.name,
                "customer": c.customer,
                "sales_officer": c.sales_officer,
                "days_pending": days,
            }
        )
    data.sort(key=lambda r: r["days_pending"], reverse=True)
    return columns, data
