import frappe


@frappe.whitelist()  # no allow_guest, login required
def get_case_state_and_history(case: str):
    """
    Return the current state + audit history of an onboarding case.
    Permission is enforced explicitly.
    """
    # 1) Explicit permission check — deny if the user has no read access to this document
    if not frappe.has_permission("Storage Onboarding Case", "read", doc=case):
        frappe.throw("You do not have access to this document", frappe.PermissionError)

    case_doc = frappe.get_doc("Storage Onboarding Case", case)

    history = frappe.get_all(
        "Onboarding Audit Log",
        filters={"onboarding_case": case},
        fields=["from_state", "to_state", "action", "user", "timestamp", "reason"],
        order_by="timestamp asc",
    )

    return {
        "case": case_doc.name,
        "customer": case_doc.customer,
        "current_state": case_doc.workflow_state,
        "total_amount": case_doc.total_amount,
        "history": history,
    }


def apply_transition(case: str, action: str, reason: str = None):
    """Apply a workflow action and record the reason in the audit log.
    Reason is passed explicitly (not stored on the doc), so no dirty state on the client.
    """
    from frappe.model.workflow import apply_workflow

    doc = frappe.get_doc("Storage Onboarding Case", case)

    # stash reason on the in-memory doc so on_update can read it (not persisted as a field change by client)
    doc.flags.transition_reason = reason
    apply_workflow(doc, action)
    return doc.workflow_state
