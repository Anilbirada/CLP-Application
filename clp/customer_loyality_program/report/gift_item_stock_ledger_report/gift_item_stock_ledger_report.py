# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    columns = [
        {"label": _("Posting Date & Time"), "fieldname": "posting_datetime", "fieldtype": "Datetime", "width": 160},
        {"label": _("Petrol Pump"), "fieldname": "petrol_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 140},
        {"label": _("Gift Item"), "fieldname": "gift_item", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": _("Transaction Type"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 140},
        {"label": _("Voucher No"), "fieldname": "voucher_no", "fieldtype": "Data", "width": 140},
        {"label": _("Qty Change"), "fieldname": "qty_change", "fieldtype": "Float", "width": 100},
        {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 110},
        {"label": _("User"), "fieldname": "user", "fieldtype": "Link", "options": "User", "width": 130},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200}
    ]
    
    conditions = []
    params = {}
    
    if filters.get("petrol_pump"):
        conditions.append("petrol_pump = %(petrol_pump)s")
        params["petrol_pump"] = filters.petrol_pump
    if filters.get("gift_item"):
        conditions.append("gift_item = %(gift_item)s")
        params["gift_item"] = filters.gift_item
    if filters.get("voucher_type"):
        conditions.append("voucher_type = %(voucher_type)s")
        params["voucher_type"] = filters.voucher_type
    if filters.get("from_date"):
        conditions.append("posting_datetime >= %(from_date)s")
        params["from_date"] = f"{filters.from_date} 00:00:00"
    if filters.get("to_date"):
        conditions.append("posting_datetime <= %(to_date)s")
        params["to_date"] = f"{filters.to_date} 23:59:59"
        
    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    
    data = frappe.db.sql(f"""
        SELECT posting_datetime, petrol_pump, gift_item, item_name, voucher_type,
               voucher_no, qty_change, balance_qty, user, remarks
        FROM `tabCLP Gift Stock Ledger`
        {where_sql}
        ORDER BY posting_datetime DESC, name DESC
    """, params, as_dict=True)
    
    total_in = sum(d.qty_change for d in data if (d.qty_change or 0) > 0)
    total_out = sum(abs(d.qty_change) for d in data if (d.qty_change or 0) < 0)
    
    summary = [
        {"label": _("Total Entries"), "value": len(data), "indicator": "Blue", "datatype": "Int"},
        {"label": _("Total Additions"), "value": total_in, "indicator": "Green", "datatype": "Float"},
        {"label": _("Total Issues / Deductions"), "value": total_out, "indicator": "Orange", "datatype": "Float"}
    ]
    
    return columns, data, None, None, summary
