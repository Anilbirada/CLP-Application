# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    days = int(filters.get("days_inactive") or 60)
    cutoff_date = frappe.utils.add_days(frappe.utils.today(), -days)
    
    columns = [
        {"label": _("Customer ID"), "fieldname": "name", "fieldtype": "Link", "options": "Loyalty Customer", "width": 140},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Mobile"), "fieldname": "mobile_number", "fieldtype": "Data", "width": 120},
        {"label": _("Vehicle"), "fieldname": "vehicle_number", "fieldtype": "Data", "width": 120},
        {"label": _("Pump"), "fieldname": "registration_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 140},
        {"label": _("Points Balance"), "fieldname": "current_cycle_liters", "fieldtype": "Float", "width": 120},
        {"label": _("Last Purchase Date"), "fieldname": "last_purchase_date", "fieldtype": "Date", "width": 150},
        {"label": _("Days Since Last Purchase"), "fieldname": "days_since", "fieldtype": "Int", "width": 170}
    ]
    
    pump_condition = ""
    params = {"cutoff_date": cutoff_date}
    if filters.get("registration_pump"):
        pump_condition = "AND c.registration_pump = %(pump)s"
        params["pump"] = filters.registration_pump
        
    data = frappe.db.sql(f"""
        SELECT 
            c.name,
            c.customer_name,
            c.mobile_number,
            c.vehicle_number,
            c.registration_pump,
            c.current_cycle_liters,
            MAX(DATE(fpe.purchase_date)) as last_purchase_date,
            DATEDIFF(CURDATE(), COALESCE(MAX(DATE(fpe.purchase_date)), DATE(c.creation))) as days_since
        FROM `tabLoyalty Customer` c
        LEFT JOIN `tabFuel Purchase Entry` fpe ON fpe.customer = c.name AND fpe.docstatus = 1
        WHERE c.status = 'Active' {pump_condition}
        GROUP BY c.name, c.customer_name, c.mobile_number, c.vehicle_number, c.registration_pump, c.current_cycle_liters, c.creation
        HAVING last_purchase_date <= %(cutoff_date)s OR (last_purchase_date IS NULL AND DATE(c.creation) <= %(cutoff_date)s)
        ORDER BY days_since DESC
        LIMIT 1000
    """, params, as_dict=True)
    
    summary = [
        {"label": _("Inactive Customers Count"), "value": len(data), "indicator": "Orange", "datatype": "Int"}
    ]
    
    return columns, data, None, None, summary
