# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    columns = [
        {"label": _("Event Date & Time"), "fieldname": "event_datetime", "fieldtype": "Datetime", "width": 170},
        {"label": _("User"), "fieldname": "actor", "fieldtype": "Link", "options": "User", "width": 160},
        {"label": _("Action"), "fieldname": "action", "fieldtype": "Data", "width": 120},
        {"label": _("Document Type"), "fieldname": "reference_doctype", "fieldtype": "Data", "width": 160},
        {"label": _("Document ID"), "fieldname": "reference_name", "fieldtype": "DynamicLink", "options": "reference_doctype", "width": 160},
        {"label": _("Details"), "fieldname": "details", "fieldtype": "Data", "width": 320}
    ]
    
    conditions = []
    params = {}
    
    if filters.get("from_datetime"):
        conditions.append("event_datetime >= %(from_datetime)s")
        params["from_datetime"] = filters.from_datetime
    if filters.get("to_datetime"):
        conditions.append("event_datetime <= %(to_datetime)s")
        params["to_datetime"] = filters.to_datetime
    if filters.get("actor"):
        conditions.append("actor = %(actor)s")
        params["actor"] = filters.actor
    if filters.get("reference_doctype"):
        conditions.append("reference_doctype = %(reference_doctype)s")
        params["reference_doctype"] = filters.reference_doctype
    if filters.get("action"):
        conditions.append("action LIKE %(action)s")
        params["action"] = f"%{filters.action}%"
        
    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    
    data = frappe.db.sql(f"""
        SELECT event_datetime, actor, action, reference_doctype, reference_name, details
        FROM `tabCLP Activity Log`
        {where_sql}
        ORDER BY event_datetime DESC
        LIMIT 2000
    """, params, as_dict=True)
    
    summary = [
        {"label": _("Total Logged Activities"), "value": len(data), "indicator": "Green", "datatype": "Int"}
    ]
    
    return columns, data, None, None, summary
