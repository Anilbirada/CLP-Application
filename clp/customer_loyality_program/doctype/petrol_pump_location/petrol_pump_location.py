# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PetrolPumpLocation(Document):
    def validate(self):
        # Update gift items with current stock
        if self.warehouse and self.gift_items:
            for item in self.gift_items:
                # Get current stock for this gift item
                stock = frappe.db.get_value("Bin",
                    {"item_code": item.gift_item, "warehouse": self.warehouse},
                    "actual_qty"
                ) or 0
                item.available_stock = stock
