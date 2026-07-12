// Copyright (c) 2026, Laida L and contributors
// For license information, please see license.txt

frappe.ui.form.on("Storage Onboarding Case", {
	before_workflow_action: (frm) => {
		const action = frm.selected_workflow_action;

		// Only Approve/Reject need a captured reason. Everything else proceeds as-is.
		if (!["Approve", "Reject"].includes(action)) {
			return;
		}

		// Reject requires a reason; Approve allows an optional note.
		const reason_required = action === "Reject";

		return new Promise((resolve, reject) => {
			let confirmed = false;

			const dialog = new frappe.ui.Dialog({
				title: __("Reason for {0}", [action]),
				fields: [
					{
						label: __("Reason"),
						fieldname: "reason",
						fieldtype: "Small Text",
						reqd: reason_required ? 1 : 0,
						description: reason_required
							? __("Required. This will be recorded in the audit log.")
							: __("Optional. This will be recorded in the audit log."),
					},
				],
				primary_action_label: __("Confirm"),
				primary_action(values) {
					confirmed = true;
					// Store the reason on the document. The SERVER (on_update) is what
					// actually writes the append-only audit log — the client only captures input.
					frm.set_value("transition_reason", values.reason || "");
					dialog.hide();
					resolve(); // allow the workflow transition to continue
				},
			});

			// Dismissing the dialog without confirming aborts the transition.
			dialog.onhide = () => {
				if (!confirmed) {
					reject();
				}
			};

			dialog.show();
		}).catch(() => {
			frappe.throw(__("Action cancelled. A reason is required to continue."));
		});
	},
});
