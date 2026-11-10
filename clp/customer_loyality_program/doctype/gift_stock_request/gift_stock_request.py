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
        """Record transfer in ERPNext and CLP Gift Stock Ledger without double movement"""
        from clp.stock import record_gift_stock_movement
        is_erpnext = "erpnext" in frappe.get_installed_apps() and frappe.db.exists("DocType", "Stock Entry")
        stock_entry_created = False

        if is_erpnext and self.source_warehouse and self.requesting_warehouse:
            try:
                company = frappe.defaults.get_defaults().get("company")
                if not company and frappe.db.exists("DocType", "Company"):
                    company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value("Company", {}, "name")

                stock_entry = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Transfer",
                    "company": company,
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
                stock_entry_created = True
            except Exception as e:
                frappe.log_error(f"ERPNext Stock Transfer creation skipped: {e}", "Gift Stock Transfer")

        # Outgoing from source pump
        record_gift_stock_movement(
            pump=self.source_pump,
            item_code=self.gift_item,
            qty_change=-float(self.quantity),
            voucher_type="Stock Transfer Out",
            voucher_no=self.name,
            remarks=f"Transfer to {self.requesting_pump}: {self.name}",
            skip_bin_sync=stock_entry_created
        )
        # Incoming to destination pump
        record_gift_stock_movement(
            pump=self.requesting_pump,
            item_code=self.gift_item,
            qty_change=float(self.quantity),
            voucher_type="Stock Transfer In",
            voucher_no=self.name,
            remarks=f"Transfer from {self.source_pump}: {self.name}",
            skip_bin_sync=stock_entry_created
        )

        self.db_set("status", "Completed")
        frappe.msgprint(_("✅ Stock transfer of {0} units recorded from {1} to {2}.").format(
            self.quantity, self.source_pump, self.requesting_pump
        ), indicator="green")

    def on_cancel(self):
        """Reverse stock transfer on cancellation and cancel ERPNext stock entry"""
        from clp.stock import record_gift_stock_movement
        has_se_cancelled = False

        if self.stock_entry:
            try:
                se = frappe.get_doc("Stock Entry", self.stock_entry)
                if se.docstatus == 1:
                    se.cancel()
                    has_se_cancelled = True
                    frappe.msgprint(_("Linked ERPNext Stock Transfer entry cancelled"), indicator="blue")
            except Exception as e:
                frappe.log_error(f"Failed to cancel stock entry {self.stock_entry}: {e}", "Gift Stock Transfer Cancel")

        record_gift_stock_movement(
            pump=self.source_pump,
            item_code=self.gift_item,
            qty_change=float(self.quantity),
            voucher_type="Stock Transfer In",
            voucher_no=self.name,
            remarks=f"Reversal of cancelled transfer to {self.requesting_pump}: {self.name}",
            skip_bin_sync=has_se_cancelled
        )
        record_gift_stock_movement(
            pump=self.requesting_pump,
            item_code=self.gift_item,
            qty_change=-float(self.quantity),
            voucher_type="Stock Transfer Out",
            voucher_no=self.name,
            remarks=f"Reversal of cancelled transfer from {self.source_pump}: {self.name}",
            skip_bin_sync=has_se_cancelled
        )
        self.db_set("status", "Cancelled")
        frappe.msgprint(_("Reversed stock transfer of {0} units.").format(self.quantity), indicator="blue")


