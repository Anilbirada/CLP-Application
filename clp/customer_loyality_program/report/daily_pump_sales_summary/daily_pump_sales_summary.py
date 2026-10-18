# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    columns = [
        {"label": _("Date"), "fieldname": "sales_date", "fieldtype": "Date", "width": 120},
        {"label": _("Petrol Pump"), "fieldname": "petrol_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 160},
        {"label": _("Pump Name"), "fieldname": "pump_name", "fieldtype": "Data", "width": 180},
        {"label": _("Total Transactions"), "fieldname": "tx_count", "fieldtype": "Int", "width": 140},
        {"label": _("Total Liters"), "fieldname": "total_liters", "fieldtype": "Float", "width": 140},
        {"label": _("Total Revenue"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 150}
    ]
    
    conditions = ["docstatus = 1"]
    params = {}
    
    if filters.get("from_date"):
        conditions.append("DATE(purchase_date) >= %(from_date)s")
        params["from_date"] = filters.from_date
    if filters.get("to_date"):
        conditions.append("DATE(purchase_date) <= %(to_date)s")
        params["to_date"] = filters.to_date
    if filters.get("petrol_pump"):
        conditions.append("petrol_pump = %(petrol_pump)s")
        params["petrol_pump"] = filters.petrol_pump
        
    where_sql = "WHERE " + " AND ".join(conditions)
    
    data = frappe.db.sql(f"""
        SELECT 
            DATE(purchase_date) as sales_date,
            petrol_pump,
            pump_name,
            COUNT(name) as tx_count,
            ROUND(SUM(liters), 2) as total_liters,
            ROUND(SUM(amount), 2) as total_amount
        FROM `tabFuel Purchase Entry`
        {where_sql}
        GROUP BY DATE(purchase_date), petrol_pump, pump_name
        ORDER BY sales_date DESC, petrol_pump ASC
    """, params, as_dict=True)
    
    grand_tx = sum(d.tx_count for d in data)
    grand_liters = sum(d.total_liters or 0 for d in data)
    grand_amount = sum(d.total_amount or 0 for d in data)
    
    summary = [
        {"label": _("Total Transactions"), "value": grand_tx, "indicator": "Blue", "datatype": "Int"},
        {"label": _("Total Liters Sold"), "value": round(grand_liters, 2), "indicator": "Green", "datatype": "Float"},
        {"label": _("Total Revenue"), "value": round(grand_amount, 2), "indicator": "Green", "datatype": "Currency"}
    ]
    
    return columns, data, None, None, summary
