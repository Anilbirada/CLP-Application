import frappe

def log_doc_event(doc, method=None):
    """Append immutable-style audit entry for important CLP document events."""
    if doc.doctype == "CLP Activity Log" or getattr(frappe.flags, "in_clp_audit_log", False):
        return
    relevant = {"Loyalty Customer", "Fuel Purchase Entry", "Gift Redemption", "Gift Stock Request", "User", "Referral Reward Entry"}
    if doc.doctype not in relevant:
        return
    try:
        frappe.flags.in_clp_audit_log = True
        event = frappe.get_doc({
            "doctype": "CLP Activity Log",
            "event_datetime": frappe.utils.now_datetime(),
            "actor": frappe.session.user or "Administrator",
            "action": method or "update",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "details": frappe.as_json({"docstatus": getattr(doc, "docstatus", None), "modified_by": getattr(doc, "modified_by", None)})
        })
        event.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "CLP Activity Audit Failure")
    finally:
        frappe.flags.in_clp_audit_log = False
