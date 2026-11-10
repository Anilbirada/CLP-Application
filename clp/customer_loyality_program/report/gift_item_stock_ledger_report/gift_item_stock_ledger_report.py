# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    columns = [
        {"label": _("Posting Date & Time"), "fieldname": "posting_datetime", "fieldtype": "Datetime", "width": 160},
        {"label": _("Petrol Pump"), "fieldname": "petrol_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 130},
        {"label": _("Gift Item"), "fieldname": "gift_item", "fieldtype": "Link", "options": "Item", "width": 130},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 160},
        {"label": _("Transaction Type"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 130},
        {"label": _("Voucher No"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 130},
        {"label": _("Qty Added"), "fieldname": "qty_added", "fieldtype": "Float", "width": 95},
        {"label": _("Qty Issued"), "fieldname": "qty_issued", "fieldtype": "Float", "width": 95},
        {"label": _("Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Loyalty Customer", "width": 130},
        {"label": _("Customer / Driver"), "fieldname": "recipient_name", "fieldtype": "Data", "width": 160},
        {"label": _("Vehicle Number"), "fieldname": "vehicle_number", "fieldtype": "Data", "width": 130},
        {"label": _("Mobile Number"), "fieldname": "mobile_number", "fieldtype": "Data", "width": 120},
        {"label": _("User"), "fieldname": "user", "fieldtype": "Link", "options": "User", "width": 120},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 180}
    ]
    
    conditions = []
    params = {}
    
    if filters.get("petrol_pump"):
        conditions.append("l.petrol_pump = %(petrol_pump)s")
        params["petrol_pump"] = filters.petrol_pump
    if filters.get("gift_item"):
        conditions.append("l.gift_item = %(gift_item)s")
        params["gift_item"] = filters.gift_item
    if filters.get("voucher_type"):
        conditions.append("l.voucher_type = %(voucher_type)s")
        params["voucher_type"] = filters.voucher_type
    if filters.get("from_date"):
        conditions.append("l.posting_datetime >= %(from_date)s")
        params["from_date"] = f"{filters.from_date} 00:00:00"
    if filters.get("to_date"):
        conditions.append("l.posting_datetime <= %(to_date)s")
        params["to_date"] = f"{filters.to_date} 23:59:59"
        
    where_sql = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    
    data = frappe.db.sql(f"""
        SELECT 
            l.posting_datetime,
            l.petrol_pump,
            l.gift_item,
            l.item_name,
            l.voucher_type,
            l.voucher_no,
            CASE WHEN l.qty_change > 0 THEN l.qty_change ELSE 0.0 END as qty_added,
            CASE WHEN l.qty_change < 0 THEN ABS(l.qty_change) ELSE 0.0 END as qty_issued,
            l.qty_change,
            l.balance_qty,
            gr.customer,
            COALESCE(gr.driver_name, gr.customer_name, c.customer_name, '') as recipient_name,
            COALESCE(gr.vehicle_number, c.vehicle_number, '') as vehicle_number,
            COALESCE(gr.customer_mobile, c.mobile_number, '') as mobile_number,
            l.user,
            l.remarks
        FROM `tabCLP Gift Stock Ledger` l
        LEFT JOIN `tabGift Redemption` gr ON gr.name = l.voucher_no AND l.voucher_type = 'Gift Redemption'
        LEFT JOIN `tabLoyalty Customer` c ON c.name = gr.customer
        {where_sql}
        ORDER BY l.posting_datetime DESC, l.name DESC
    """, params, as_dict=True)
    
    total_in = sum(d.get("qty_added") or 0.0 for d in data)
    total_out = sum(d.get("qty_issued") or 0.0 for d in data)
    
    summary = [
        {"label": _("Total Entries"), "value": len(data), "indicator": "Blue", "datatype": "Int"},
        {"label": _("Total Additions"), "value": total_in, "indicator": "Green", "datatype": "Float"},
        {"label": _("Total Issues / Deductions"), "value": total_out, "indicator": "Orange", "datatype": "Float"}
    ]
    
    return columns, data, None, None, summary

