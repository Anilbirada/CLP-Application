# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def record_gift_stock_movement(pump, item_code, qty_change, voucher_type, voucher_no=None, remarks=None, user=None, skip_bin_sync=False):
    """
    Record an immutable stock movement entry in CLP Gift Stock Ledger.
    Single Source of Truth:
    - If ERPNext is installed, inventory quantities are managed exclusively via ERPNext Stock Entries
      (Material Receipt, Material Issue, Material Transfer). Direct Bin updates are avoided to prevent
      double inventory deductions.
    - If ERPNext is not installed (standalone CLP environment), fallback to synchronizing tabBin.
    - NEVER call frappe.db.commit() directly: let Frappe's database transaction manager ensure atomicity.
    """
    if not pump or not item_code or qty_change == 0:
        return None

    user = user or frappe.session.user or "Administrator"
    now = frappe.utils.now_datetime()
    
    item_name = frappe.db.get_value("Item", item_code, "item_name") if frappe.db.exists("DocType", "Item") else item_code
    item_name = item_name or item_code

    # Calculate new running balance for this pump & gift item
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
        "item_name": item_name,
        "voucher_type": voucher_type,
        "voucher_no": voucher_no or "",
        "qty_change": float(qty_change),
        "balance_qty": new_balance,
        "user": user,
        "remarks": remarks or ""
    })
    ledger_entry.flags.ignore_permissions = True
    ledger_entry.insert()

    # Synchronize tabBin ONLY if ERPNext is NOT handling stock (prevent double movement)
    is_erpnext_installed = "erpnext" in frappe.get_installed_apps()
    if not is_erpnext_installed and not skip_bin_sync:
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
            # Notice: No manual frappe.db.commit() - transaction is managed atomically by Frappe caller

    return ledger_entry


def get_pump_gift_stock_balance(pump, item_code=None):
    """
    Return current gift stock balance for a pump.
    Uses ERPNext tabBin if ERPNext is present; otherwise computes from tabCLP Gift Stock Ledger.
    """
    if not pump:
        return 0.0 if item_code else {}

    warehouse = frappe.db.get_value("Petrol Pump Location", pump, "warehouse")
    is_erpnext = "erpnext" in frappe.get_installed_apps() and warehouse

    if is_erpnext:
        if item_code:
            qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
            return float(qty or 0.0)
        else:
            rows = frappe.db.sql("""
                SELECT item_code, actual_qty as balance
                FROM `tabBin`
                WHERE warehouse = %s
            """, (warehouse,), as_dict=True)
            return {r.item_code: float(r.balance or 0.0) for r in rows}

    # Standalone CLP calculation from CLP Gift Stock Ledger
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
