# Storage Onboarding — Custom Frappe App (`cryo_onboarding`)

A custom Frappe app that manages the client **onboarding approval lifecycle** for long-term storage sign-ups, from CRM handover through to "ready for storage agreement". It replaces the current email-based approval process with a structured, permissioned, and fully auditable workflow inside ERPNext.

This is the **default CryoCord scenario**: a Sales Officer prepares an onboarding case (requested packages, pricing, discounts) and submits it for review; an Operations Manager approves or rejects it; every state transition is recorded in an append-only audit log with who / when / from-state / to-state / reason.

---

## Table of contents

- [Setup](#setup)
- [Data model](#data-model)
- [Workflow & server-side logic](#workflow--server-side-logic)
- [Permissions](#permissions)
- [Audit trail](#audit-trail)
- [Report & API](#report--api)
- [Upgrade-safety](#upgrade-safety)
- [Design rationale](#design-rationale)
- [Role & permission matrix](#role--permission-matrix)
- [Production-readiness note](#production-readiness-note)
- [What I tested](#what-i-tested)
- [Assumptions](#assumptions)
- [What I would do with more time](#what-i-would-do-with-more-time)

---

## Setup

Tested on **ERPNext v15** (Frappe v15). The app depends on ERPNext because it reuses the standard `Customer` DocType.

```bash
# 1. From your bench directory, get the app
bench get-app $URL_OF_THIS_REPO --branch main

# 2. Install it on a site that already has ERPNext installed
bench --site <your-site> install-app cryo_onboarding

# 3. Run migrate to sync fixtures (roles, permissions, workflow, custom fields)
bench --site <your-site> migrate
```

After migrate, the following are created automatically via fixtures: the roles **Sales Officer** and **Operations Manager**, their document-level permissions, the **Storage Onboarding Workflow** (states, transitions, actions), and the `workflow_state` custom field.

To try it out, create at least one `Customer`, assign the two roles to two different users, and create a `Storage Onboarding Case`.

---

## Data model

Three custom DocTypes, plus reuse of the standard ERPNext `Customer`.

```
Customer (standard ERPNext)  ◄── linked by
        │
Storage Onboarding Case  (parent — one onboarding request)
   ├─ customer            → Link → Customer (mandatory)
   ├─ sales_officer       → Link → User (auto-set to the creator)
   ├─ workflow_state      → managed by Frappe Workflow (auto-created)
   ├─ total_amount        → Currency (computed, read-only)
   ├─ transition_reason   → Small Text (hidden buffer; see Audit trail)
   └─ requested_packages  → Table → Storage Package Request  (child)
                               ├─ package
                               ├─ qty
                               ├─ rate
                               ├─ discount_percent
                               └─ amount  (computed)

Onboarding Audit Log  (standalone DocType — append-only)
   ├─ onboarding_case  → Link → Storage Onboarding Case
   ├─ from_state
   ├─ to_state
   ├─ action
   ├─ user             (who)
   ├─ timestamp        (when)
   └─ reason
```

Naming series: `Storage Onboarding Case` → `SOC-.YYYY.-.#####`; `Onboarding Audit Log` → `OAL-.YYYY.-.#####`.

**The case is deliberately NOT submittable.** Its lifecycle is managed entirely by Frappe Workflow via `workflow_state`, so there is a single source of truth for status. Adding `docstatus` (submit/cancel) would create a second, overlapping state machine that must be kept in sync — a source of ambiguity and bugs. Immutability (normally provided by submit) is enforced explicitly in Python based on `workflow_state` instead.

---

## Workflow & server-side logic

**States:** `Draft → Pending Approval → Approved / Rejected → Ready for Agreement → Closed`.
`Rejected` can return to `Draft` for revision.

The workflow (states, transitions, allowed roles) is defined as a Frappe **Workflow** and drives the UI. **But the workflow is not trusted as the only guard** — every rule below is enforced server-side in the DocType controller (`storage_onboarding_case.py`), so it holds even if a transition is driven directly through the API rather than the UI:

- **Illegal transitions are blocked** against an explicit `ALLOWED_TRANSITIONS` map in `validate()`. Any save that moves `workflow_state` to a state not reachable from the current one is rejected (e.g. `Draft → Closed`).
- **Separation of duties:** the creator (`owner`) cannot approve or reject their own case — enforced in Python (`frappe.session.user == self.owner`) _and_ by unchecking "Allow Self Approval" on the Approve/Reject transitions.
- **Business rules:** cannot approve with no line items; quantities and rates cannot be negative; a reason is mandatory when rejecting.
- **Immutability:** once a case is `Approved`, `Ready for Agreement`, or `Closed`, it cannot be edited (workflow "Only Allow Edit For" points to System Manager, not the business roles) and cannot be deleted (`on_trash` guard).

Line amounts and the case total are computed server-side in `validate()` (`amount = qty × rate × (1 − discount%/100)`), so the numbers cannot be tampered with from the client.

### Reason capture (design note)

A transition reason is an attribute of the **transition event**, not of the case document. The client shows a small dialog on Approve/Reject and writes the reason to `transition_reason` **before** the workflow action runs (the workflow engine reloads the doc from the DB, so the value must already be persisted). The server's `on_update` copies that reason into the audit log and then clears `transition_reason`, so it never carries over to a later transition. The field is hidden from the form; it is a short-lived buffer, not user input.

---

## Permissions

Two business roles, **Sales Officer** and **Operations Manager**, enforced at the document/server level (not by hiding fields or buttons):

- Frappe evaluates `has_permission` on the server for every read, write, report, and API call. A user without read permission never receives the data — it is not fetched, not merely hidden.
- **Sales Officer** has create/write with **"Only If Creator"**, so a Sales Officer can only touch cases they created.
- **Operations Manager** has read/write across all cases (needed to review and approve) but no create and no delete.
- Both roles are granted **read-only** on `Customer` so they can link a customer but cannot modify the customer master.
- `Onboarding Audit Log` is **read-only** for both business roles; entries are created only by trusted server code.

See the full [role & permission matrix](#role--permission-matrix) below.

---

## Audit trail

Every important state transition is recorded as a **separate `Onboarding Audit Log` record** — not as document versioning, and not as a child table.

- It is created server-side in `on_update` whenever `workflow_state` changes, capturing `from_state`, `to_state`, `action`, `user` (`frappe.session.user`, not client-supplied), `timestamp`, and `reason`.
- It is a **standalone DocType** (not a child of the case) so it is genuinely append-only: child rows are rewritten on every parent save, whereas a standalone record is independent, individually addressable, and queryable across all cases (needed for reporting).
- Business roles have **read-only** access; there is no UI or normal API path for them to create, edit, or delete entries.

### What the audit trail guarantees — and what it does not

**Guarantees (application level):** every state transition performed through the application (UI, REST, or the workflow engine) produces one immutable log entry attributing the action to the authenticated user, with the reason captured at that moment. Business-role users cannot forge, edit, or delete entries.

**Does NOT guarantee (be honest):**

- A **database administrator** or anyone with direct MariaDB access can still `UPDATE`/`DELETE` rows. Application-level append-only cannot prevent this.
- A **System Manager** with server/console access can run arbitrary code and could fabricate or remove entries.
- The audit is written in the same transaction as the transition; it is not an independent, external, or cryptographically verifiable record.

**How I would harden it in production:** hash-chain each entry (store a hash of the previous entry so any tampering is detectable), and/or mirror the log to an append-only external / WORM store; restrict production DB access; and consider signing entries. See [What I would do with more time](#what-i-would-do-with-more-time).

---

## Report & API

**Report — "Pending Approvals by Age"** (Script Report): lists cases currently in `Pending Approval`, sorted by how long they have been waiting, so managers can see what is stuck.

**Whitelisted REST API — `get_case_state_and_history`** (`cryo_onboarding/api.py`): returns a case's current state plus its full audit history.

```
GET /api/method/cryo_onboarding.api.get_case_state_and_history?case=SOC-2026-00001
```

- Uses `@frappe.whitelist()` and is **not** `allow_guest`, so authentication is required.
- Performs an **explicit permission check** (`frappe.has_permission("Storage Onboarding Case", "read", doc=case)`) and raises `PermissionError` otherwise, so it does not leak data across permissions.

---

## Upgrade-safety

Everything is a proper custom app — no edits to ERPNext core — so it survives ERPNext upgrades:

- **DocTypes** are stored as JSON + Python controllers in the app and versioned in Git.
- **Business logic** lives in the app's Python controllers.
- **Roles, document permissions (Custom DocPerm), the Workflow (states/transitions/actions), and the `workflow_state` custom field** are exported as **fixtures** and re-synced on every `bench migrate`.
- **One-time data transformations** (if ever needed) would be handled by **patches**, not fixtures.

Because nothing in ERPNext core is modified, an upgrade replaces core while this app is untouched; `bench migrate` re-applies the app's schema and fixtures.

---

## Design rationale

**1. Why reuse `Customer` instead of creating a client master?**
A CryoCord client is a customer in the full business sense — with contacts, addresses, and downstream transactions (invoices, payments) that ERPNext's `Customer` already models and integrates. Creating a parallel client master would duplicate that, break those integrations, and split client data in two. The onboarding case only needs to _reference_ which client, so it links to `Customer`. A custom DocType was created only for what genuinely does not exist in ERPNext: the onboarding approval process itself.

**2. When did I use a child table vs a separate linked DocType, and why?**
`Storage Package Request` is a **child table** because a requested package has no independent identity and lives and dies with its parent case — nobody queries a single requested line across cases as a standalone entity. `Onboarding Audit Log` is a **separate DocType** for the opposite reasons: it must be genuinely append-only (child rows are rewritten on every parent save), it must be queryable across all cases (for the report), and it needs its own read-only permissions.

**3. Frappe Workflow exists — why is server-side validation still necessary?**
Frappe Workflow only guards transitions that go _through the workflow action API_. Business rules, separation of duties, and legal-transition checks must therefore also live in the controller (`validate` / `on_update`), which runs on every save regardless of how it was triggered (UI, REST, workflow engine). The workflow provides UX and the happy path; the Python controller is the actual guarantee. (Note: a _raw_ `frappe.db.set_value` on the state field bypasses ORM hooks — the intended hardening is a single whitelisted transition entrypoint; see [What I would do with more time](#what-i-would-do-with-more-time).)

**4. How are permissions enforced beyond hiding fields or buttons?**
Through Frappe Role Permissions, which are enforced at the query/document level on the server — a user without read permission never receives the data. "Only If Creator" restricts Sales Officers to their own cases. This is layered with the audit log being read-only and the separation-of-duties check in Python, so protection is defence-in-depth, not cosmetic.

**5. What does the audit trail guarantee, and what does it not?**
See [Audit trail](#audit-trail). In short: at the application level it guarantees an immutable, attributed record of every transition that business users cannot forge or alter; it does **not** protect against a DBA or System Manager with direct database/server access. Hardening options are documented.

**6. How does the app stay upgrade-safe?**
See [Upgrade-safety](#upgrade-safety). Everything is a custom app with hooks, fixtures, and (where needed) patches; ERPNext core is never modified, so upgrades leave the app intact and `bench migrate` re-applies its schema and fixtures.

---

## Role & permission matrix

| Business role      | Frappe role          | Create | Edit (Draft)  | Approve | Reject | Close | Allowed workflow transitions                                                                             | Enforced by                                                                                                                                                |
| ------------------ | -------------------- | ------ | ------------- | ------- | ------ | ----- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sales Officer      | `Sales Officer`      | ✅     | ✅ (own only) | ❌      | ❌     | ❌    | `Draft → Pending Approval`, `Rejected → Draft`                                                           | Role Permissions (create/write + _Only If Creator_) + Workflow (allowed role) + Python (transition guard)                                                  |
| Operations Manager | `Operations Manager` | ❌     | ❌            | ✅      | ✅     | ✅    | `Pending Approval → Approved/Rejected`, `Approved → Ready for Agreement`, `Ready for Agreement → Closed` | Role Permissions (read/write, no create/delete) + Workflow (allowed role, self-approval off) + Python (separation of duties, business rules, immutability) |

Notes:

- **Separation of duties** (`owner` cannot approve/reject own): Workflow ("Allow Self Approval" unchecked) **and** Python (`frappe.session.user == self.owner`).
- **Immutability** of `Approved` / `Ready for Agreement` / `Closed`: Workflow ("Only Allow Edit For" = System Manager, not a business role) **and** Python (`on_trash` guard, `ALLOWED_TRANSITIONS`).
- **Audit log**: read-only for both roles; inserted only by server code.
- **Customer**: read-only for both roles (needed to link, not to modify).

---

## Production-readiness note

**What happens during `bench migrate`:** the app's DocType schema is synced, its fixtures are re-applied idempotently, and any pending patches run once. **Fixtures synced:** `Role` (Sales Officer, Operations Manager), `Custom DocPerm` for the app's DocTypes and the Customer read grant, `Workflow` + `Workflow State` + `Workflow Action Master`, and the `Custom Field` `workflow_state`. **Fixture vs patch:** use a **fixture** for configuration/master data that should always be present and is idempotent (roles, permissions, workflow); use a **patch** for one-time data transformations that a fixture cannot express (e.g. backfilling or renaming a field on existing records).

**Before applying in production:** take a full backup with files (`bench --site <site> backup --with-files`), keep an off-site copy, and run the migration on a staging copy first. **If something goes wrong:** restore from the pre-migration backup (`bench --site <site> restore <backup-file>`) to roll back to the last known-good snapshot. (Backup/restore is described, not implemented — it is standard bench tooling.)

---

## What I tested

Verified manually with dedicated test users (a Sales Officer, an Operations Manager, and a user holding both roles), not as Administrator (who bypasses permissions):

- Full lifecycle `Draft → … → Closed`; amount/total auto-calculation; naming series.
- Audit log written for every transition, with the correct reason from the dialog.
- **Separation of duties**: the workflow hides Approve for the creator; the Python guard rejects a forced approval via the API; a non-creator Operations Manager can approve normally.
- Reject requires a reason; approve with no line items is rejected; negative qty/rate is rejected.
- "Only If Creator": a Sales Officer sees only their own cases; an Operations Manager sees all.
- Immutability: `Approved`/`Closed` cannot be edited via the UI; delete is rejected by `on_trash` even for a user with delete rights (tested via `bench console`).
- Illegal transitions (e.g. `Draft → Closed`) blocked server-side via `bench console`.
- API returns state + history for an authorised user and raises `PermissionError` for an unauthorised one.
- "Pending Approvals by Age" report lists and sorts pending cases.

---

## Assumptions

- ERPNext v15 with a `Customer` master available; the onboarding process is the sales/admin approval only — it does not create the final storage agreement, handle billing, or model the lab/storage itself.
- The two business roles are sufficient for the scenario; System Manager remains the administrative role.
- "Ready for Agreement" is a deliberate handover state between "approved" and "closed"; it can be collapsed if no downstream handover step is needed.
- Currency/number formatting follows the site default and is not part of the assessment scope.

---

## What I would do with more time

- **Single whitelisted transition entrypoint** (`apply_transition(case, action, reason)`) so the reason is passed atomically and a raw `db.set_value` on `workflow_state` cannot bypass the guards — closing the last server-side gap noted in rationale #3.
- **Tamper-evident audit**: hash-chain entries and/or mirror to an append-only external store; sign entries.
- **More accurate "days pending"** computed from the audit entry that first moved the case into `Pending Approval`, rather than `modified`.
- **Automated tests** (unit tests for the guards, separation of duties, and the API).
- **Optional webhook** on transition; print format / PDF for the approved case; richer reporting (e.g. "Approved Cases by Client").
