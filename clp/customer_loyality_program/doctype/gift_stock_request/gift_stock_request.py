# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GiftStockRequest(Document):
    def validate(self):
        if not self.quantity or self.quantity <= 0:
            frappe.throw(_("Transfer quantity must be greater than zero"))
        if not self.source_warehouse or not self.requesting_warehouse:
            frappe.throw(_("Source and destination warehouses are required"))
        if self.source_warehouse == self.requesting_warehouse:
            frappe.throw(_("Source and destination warehouses must be different"))
        source_pump_warehouse = frappe.db.get_value("Petrol Pump Location", self.source_pump, "warehouse") if self.source_pump else None
        target_pump_warehouse = frappe.db.get_value("Petrol Pump Location", self.requesting_pump, "warehouse") if self.requesting_pump else None
        if not source_pump_warehouse or source_pump_warehouse != self.source_warehouse:
            frappe.throw(_("Source warehouse must match the source pump"))
        if not target_pump_warehouse or target_pump_warehouse != self.requesting_warehouse:
            frappe.throw(_("Destination warehouse must match the requesting pump"))

        # Get stock availability
        if self.source_warehouse and self.gift_item:
            self.available_stock = frappe.db.get_value("Bin",
                {"item_code": self.gift_item, "warehouse": self.source_warehouse},
                "actual_qty"
            ) or 0
            
        if self.requesting_warehouse and self.gift_item:
            self.current_stock_requesting = frappe.db.get_value("Bin",
                {"item_code": self.gift_item, "warehouse": self.requesting_warehouse},
                "actual_qty"
            ) or 0
        
        # Validate quantity
        if self.quantity and self.quantity > (self.available_stock or 0):
            frappe.throw(_("Requested quantity {0} exceeds available stock {1} at source pump").format(
                self.quantity, self.available_stock
            ))
    
    def before_submit(self):
        """Only owner/admin or users explicitly assigned stock-transfer permission can submit."""
        if self.status == "Approved" and not (
            {"System Manager", "Pump Owner", "CLP Stock Transfer"} & set(frappe.get_roles())
        ):
            frappe.throw(_("You do not have permission to approve/execute stock transfers"), frappe.PermissionError)

    def on_submit(self):
        """Create Stock Entry on approval"""
        if self.status == "Approved" and not self.stock_entry:
            self.create_stock_entry()
    
    def create_stock_entry(self):
        """Record transfer in CLP Gift Stock Ledger and optional ERPNext stock entry"""
        from clp.stock import record_gift_stock_movement
        # Outgoing from source pump
        record_gift_stock_movement(
            pump=self.source_pump,
            item_code=self.gift_item,
            qty_change=-float(self.quantity),
            voucher_type="Stock Transfer Out",
            voucher_no=self.name,
            remarks=f"Transfer to {self.requesting_pump}: {self.name}"
        )
        # Incoming to destination pump
        record_gift_stock_movement(
            pump=self.requesting_pump,
            item_code=self.gift_item,
            qty_change=float(self.quantity),
            voucher_type="Stock Transfer In",
            voucher_no=self.name,
            remarks=f"Transfer from {self.source_pump}: {self.name}"
        )

        try:
            if frappe.db.exists("DocType", "Stock Entry"):
                stock_entry = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Transfer",
                    "is_gift_transfer": 1,
                    "from_pump": self.source_pump,
                    "to_pump": self.requesting_pump,
                    "transfer_notes": f"Gift Stock Request: {self.name}\n{self.notes or ''}",
                    "items": [{
                        "item_code": self.gift_item,
                        "qty": self.quantity,
                        "s_warehouse": self.source_warehouse,
                        "t_warehouse": self.requesting_warehouse
                    }]
                })
                stock_entry.flags.ignore_permissions = True
                stock_entry.insert()
                stock_entry.submit()
                self.db_set("stock_entry", stock_entry.name)
        except Exception as e:
            frappe.log_error(f"Optional ERPNext Stock Entry skipped: {e}", "Gift Stock Transfer")

        self.db_set("status", "Completed")
        frappe.msgprint(_("✅ Stock transfer of {0} units recorded from {1} to {2}.").format(
            self.quantity, self.source_pump, self.requesting_pump
        ), indicator="green")

    def on_cancel(self):
        """Reverse stock transfer on cancellation"""
        from clp.stock import record_gift_stock_movement
        record_gift_stock_movement(
            pump=self.source_pump,
            item_code=self.gift_item,
            qty_change=float(self.quantity),
            voucher_type="Stock Transfer In",
            voucher_no=self.name,
            remarks=f"Reversal of cancelled transfer to {self.requesting_pump}: {self.name}"
        )
        record_gift_stock_movement(
            pump=self.requesting_pump,
            item_code=self.gift_item,
            qty_change=-float(self.quantity),
            voucher_type="Stock Transfer Out",
            voucher_no=self.name,
            remarks=f"Reversal of cancelled transfer from {self.source_pump}: {self.name}"
        )
        frappe.msgprint(_("Reversed stock transfer of {0} units.").format(self.quantity), indicator="blue")

