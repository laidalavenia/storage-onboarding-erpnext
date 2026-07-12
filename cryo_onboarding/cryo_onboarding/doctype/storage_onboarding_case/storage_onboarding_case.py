# Copyright (c) 2026, Laida L and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

ALLOWED_TRANSITIONS = {
    "Draft": {"Pending Approval"},
    "Pending Approval": {"Approved", "Rejected"},
    "Rejected": {"Draft"},
    "Approved": {"Ready for Agreement"},
    "Ready for Agreement": {"Closed"},
    "Closed": set(),
}

IMMUTABLE_STATES = {"Approved", "Ready for Agreement", "Closed"}


class StorageOnboardingCase(Document):
    def validate(self):
        self._set_defaults()
        self._validate_line_items()
        self._guard_state_transition()

    def _set_defaults(self):
        if not self.sales_officer:
            self.sales_officer = self.owner

    def _validate_line_items(self):
        total = 0
        for row in self.requested_packages:
            if (row.qty or 0) < 0 or (row.rate or 0) < 0:
                frappe.throw("Qty/Rate cannot be negative")
            discount = row.discount_percent or 0
            row.amount = (row.qty or 0) * (row.rate or 0) * (1 - discount / 100.0)
            total += row.amount
        self.total_amount = total

    def _guard_state_transition(self):
        # new document must start in Draft
        if self.is_new():
            if self.workflow_state and self.workflow_state != "Draft":
                frappe.throw("A new document must start in Draft")
            return

        before = self.get_doc_before_save()
        if not before:
            return
        old = before.workflow_state
        new = self.workflow_state
        if old == new:
            return  # not a state transition, skip

        # 1) Block illegal transitions — runs NO MATTER HOW the doc is saved (including direct API writes)
        if new not in ALLOWED_TRANSITIONS.get(old, set()):
            frappe.throw(f"Illegal transition: {old} → {new}")

        # 2) Cannot approve with no line items
        if new == "Approved" and not self.requested_packages:
            frappe.throw("Cannot approve a case with no package items")

        # 3) Separation of duties — the creator cannot approve/reject their own document
        if new in ("Approved", "Rejected") and frappe.session.user == self.owner:
            frappe.throw(
                "The creator of a case cannot approve or reject their own document"
            )

        # 4) A reason is mandatory when rejecting
        if new == "Rejected" and not (self.transition_reason or "").strip():
            frappe.throw("A reason is required to reject")

    def on_update(self):
        # Write an audit entry ONLY when the state actually changes
        before = self.get_doc_before_save()
        if not before:
            return
        old = before.workflow_state
        new = self.workflow_state
        if old == new:
            return

        frappe.get_doc(
            {
                "doctype": "Onboarding Audit Log",
                "onboarding_case": self.name,
                "from_state": old,
                "to_state": new,
                "action": f"{old} → {new}",
                "user": frappe.session.user,
                "timestamp": now_datetime(),
                "reason": self.transition_reason or "",
            }
        ).insert(
            ignore_permissions=True
        )  # users have no Create on the log; this is server-only

        # Clear the reason so it does not carry over to the next transition
        self.db_set("transition_reason", None, update_modified=False)

    def on_trash(self):
        if self.workflow_state in IMMUTABLE_STATES:
            frappe.throw("Approved/closed cases cannot be deleted")
