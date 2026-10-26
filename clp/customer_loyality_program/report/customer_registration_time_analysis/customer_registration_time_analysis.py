# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_datetime

def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.start_datetime or not filters.end_datetime:
        frappe.throw(_("Start and end date/time are required."))
    
    start = get_datetime(filters.start_datetime)
    end = get_datetime(filters.end_datetime)
    
    if end < start:
        frappe.throw(_("End date/time must be after or equal to start date/time."))
        
    columns = [
        {"label": _("Customer ID"), "fieldname": "name", "fieldtype": "Link", "options": "Loyalty Customer", "width": 140},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 170},
        {"label": _("Mobile"), "fieldname": "mobile_number", "fieldtype": "Data", "width": 120},
        {"label": _("Vehicle"), "fieldname": "vehicle_number", "fieldtype": "Data", "width": 120},
        {"label": _("Registration Pump"), "fieldname": "registration_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 150},
        {"label": _("Registered At"), "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": _("Created By"), "fieldname": "created_by_user", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": _("Current Cycle Liters"), "fieldname": "current_cycle_liters", "fieldtype": "Float", "width": 140},
        {"label": _("Total Liters"), "fieldname": "total_liters_purchased", "fieldtype": "Float", "width": 130}
    ]
    
    conditions = ["creation >= %(start)s", "creation <= %(end)s"]
    params = {"start": start, "end": end}
    
    if filters.get("registration_pump"):
        conditions.append("registration_pump = %(registration_pump)s")
        params["registration_pump"] = filters.registration_pump
        
    data = frappe.db.sql(
        """
        SELECT 
            name, 
            customer_name, 
            mobile_number, 
            vehicle_number, 
            registration_pump,
            creation, 
            created_by_user,
            current_cycle_liters,
            total_liters_purchased
        FROM `tabLoyalty Customer` 
        WHERE """ + " AND ".join(conditions) + """ 
        ORDER BY creation DESC
        """,
        params, as_dict=True
    )
    
    total_liters = sum(flt(d.get("total_liters_purchased") or 0) for d in data)
    summary = [
        {"label": _("Total Registrations"), "value": len(data), "indicator": "Green", "datatype": "Int"},
        {"label": _("Total Liters Purchased"), "value": round(total_liters, 2), "indicator": "Blue", "datatype": "Float"}
    ]
    
    return columns, data, None, None, summary
