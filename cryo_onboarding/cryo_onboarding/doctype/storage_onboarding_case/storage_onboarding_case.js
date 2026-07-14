// Copyright (c) 2026, Laida L and contributors
// For license information, please see license.txt

frappe.ui.form.on("Storage Onboarding Case", {
	before_workflow_action: (frm) => {
		const action = frm.selected_workflow_action;

		if (!["Approve", "Reject"].includes(action)) {
			return;
		}

		const reason_required = action === "Reject";

		return new Promise((resolve, reject) => {
			frappe.dom.unfreeze();

			frappe.prompt(
				[
					{
						label: __("Reason"),
						fieldname: "reason",
						fieldtype: "Small Text",
						reqd: reason_required ? 1 : 0,
					},
				],
				(values) => {
					const reason = values.reason || "";
					frappe.db
						.set_value(
							"Storage Onboarding Case",
							frm.doc.name,
							"transition_reason",
							reason,
						)
						.then(() => resolve())
						.catch(() => reject());
				},
				__("Reason for {0}", [action]),
				__("Confirm"),
			);
		});
	},
});
