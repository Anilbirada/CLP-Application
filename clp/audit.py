import frappe

def log_doc_event(doc, method=None):
    """Append immutable-style audit entry for important CLP document events."""
    if doc.doctype == "CLP Activity Log" or getattr(frappe.flags, "in_clp_audit_log", False):
        return
    relevant = {
        "Loyalty Customer",
        "Fuel Purchase Entry",
        "Gift Redemption",
        "Gift Stock Request",
        "User",
        "Referral Reward Entry",
        "CLP Customer Balance Adjustment"
    }
    if doc.doctype not in relevant:
        return
    try:
        frappe.flags.in_clp_audit_log = True
        
        details_dict = {
            "docstatus": getattr(doc, "docstatus", None),
            "modified_by": getattr(doc, "modified_by", None),
            "method": method
        }

        if doc.doctype == "CLP Customer Balance Adjustment":
            details_dict.update({
                "customer": getattr(doc, "customer", None),
                "adjustment_type": getattr(doc, "adjustment_type", None),
                "points": getattr(doc, "points", 0),
                "previous_balance": getattr(doc, "previous_balance", 0),
                "new_balance": getattr(doc, "new_balance", 0),
                "reason": getattr(doc, "reason", None),
                "notes": getattr(doc, "notes", None)
            })
        elif doc.doctype == "Fuel Purchase Entry":
            details_dict.update({
                "customer": getattr(doc, "customer", None),
                "liters": getattr(doc, "liters", 0),
                "petrol_pump": getattr(doc, "petrol_pump", None),
                "slip_no": getattr(doc, "slip_no", None)
            })
        elif doc.doctype == "Gift Redemption":
            details_dict.update({
                "customer": getattr(doc, "customer", None),
                "total_points": getattr(doc, "total_points", 0),
                "petrol_pump": getattr(doc, "petrol_pump", None)
            })
        elif doc.doctype == "Gift Stock Request":
            details_dict.update({
                "petrol_pump": getattr(doc, "petrol_pump", None),
                "status": getattr(doc, "status", None)
            })
        elif doc.doctype == "Loyalty Customer":
            details_dict.update({
                "customer_name": getattr(doc, "customer_name", None),
                "vehicle_number": getattr(doc, "vehicle_number", None),
                "status": getattr(doc, "status", None),
                "registration_pump": getattr(doc, "registration_pump", None)
            })

        event = frappe.get_doc({
            "doctype": "CLP Activity Log",
            "event_datetime": frappe.utils.now_datetime(),
            "actor": frappe.session.user or "Administrator",
            "action": method or "update",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "details": frappe.as_json(details_dict)
        })
        event.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "CLP Activity Audit Failure")
    finally:
        frappe.flags.in_clp_audit_log = False
