# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CLPGiftStockLedger(Document):
    def before_insert(self):
        # Enforce approved owner-only stock addition policy
        user_roles = frappe.get_roles(frappe.session.user)
        allowed = {"System Manager", "Pump Owner", "CLP Stock Add", "Administrator"}
        if not (set(user_roles) & allowed):
            frappe.throw(
                frappe._("Permission Denied: Only Pump Owners or System Managers are authorized to create Gift Stock Ledger additions."),
                frappe.PermissionError
            )

    def validate(self):
        if not self.posting_datetime:
            self.posting_datetime = frappe.utils.now_datetime()
        if not self.user:
            self.user = frappe.session.user
            
        # Compute running balance for this pump and gift item
        prev_balance = frappe.db.sql("""
            SELECT COALESCE(SUM(qty_change), 0)
            FROM `tabCLP Gift Stock Ledger`
            WHERE petrol_pump = %s AND gift_item = %s AND name != %s
        """, (self.petrol_pump, self.gift_item, self.name or ""))
        
        current_sum = float(prev_balance[0][0]) if prev_balance else 0.0
        self.balance_qty = current_sum + float(self.qty_change or 0.0)
