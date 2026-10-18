# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CLPGiftStockLedger(Document):
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
