# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe

def record_gift_stock_movement(pump, item_code, qty_change, voucher_type, voucher_no=None, remarks=None, user=None):
    """Record an immutable stock movement entry in CLP Gift Stock Ledger and sync tabBin if present."""
    if not pump or not item_code or qty_change == 0:
        return None

    user = user or frappe.session.user or "Administrator"
    now = frappe.utils.now_datetime()
    
    # Calculate new running balance
    prev_balance = frappe.db.sql("""
        SELECT COALESCE(SUM(qty_change), 0)
        FROM `tabCLP Gift Stock Ledger`
        WHERE petrol_pump = %s AND gift_item = %s
    """, (pump, item_code))[0][0] or 0.0
    
    new_balance = float(prev_balance) + float(qty_change)
    
    ledger_entry = frappe.get_doc({
        "doctype": "CLP Gift Stock Ledger",
        "posting_datetime": now,
        "petrol_pump": pump,
        "gift_item": item_code,
        "voucher_type": voucher_type,
        "voucher_no": voucher_no or "",
        "qty_change": float(qty_change),
        "balance_qty": new_balance,
        "user": user,
        "remarks": remarks or ""
    })
    ledger_entry.flags.ignore_permissions = True
    ledger_entry.insert()

    # Also keep tabBin actual_qty synchronized for the pump's warehouse
    warehouse = frappe.db.get_value("Petrol Pump Location", pump, "warehouse")
    if warehouse and (frappe.db.table_exists("Bin") or frappe.db.table_exists("tabBin")):
        bin_name = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "name")
        if bin_name:
            frappe.db.sql("""
                UPDATE `tabBin`
                SET actual_qty = actual_qty + %s, modified = %s
                WHERE name = %s
            """, (qty_change, now, bin_name))
        else:
            frappe.db.sql("""
                INSERT INTO `tabBin` (name, creation, modified, modified_by, owner, docstatus, item_code, warehouse, actual_qty)
                VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s)
            """, (frappe.generate_hash(length=10), now, now, user, user, item_code, warehouse, qty_change))
        frappe.db.commit()
            
    return ledger_entry


def get_pump_gift_stock_balance(pump, item_code=None):
    """Return current gift stock balance for a pump, either for a specific item or all items."""
    if item_code:
        balance = frappe.db.sql("""
            SELECT COALESCE(SUM(qty_change), 0)
            FROM `tabCLP Gift Stock Ledger`
            WHERE petrol_pump = %s AND gift_item = %s
        """, (pump, item_code))[0][0] or 0.0
        return float(balance)
    
    rows = frappe.db.sql("""
        SELECT gift_item, COALESCE(SUM(qty_change), 0) as balance
        FROM `tabCLP Gift Stock Ledger`
        WHERE petrol_pump = %s
        GROUP BY gift_item
    """, (pump,), as_dict=True)
    return {r.gift_item: float(r.balance) for r in rows}
