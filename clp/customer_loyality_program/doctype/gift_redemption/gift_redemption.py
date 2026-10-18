# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GiftRedemption(Document):
    def before_insert(self):
        """Auto-set gift_given_by"""
        if not self.gift_given_by:
            self.gift_given_by = frappe.session.user
    
    def before_validate(self):
        """Prevent validation on cancel/update after submit"""
        if self.docstatus == 1 and self.flags.ignore_validate:
            return
    
    def validate(self):
        """Validate redemption - ALLOW NEGATIVE BALANCE"""
        # Skip validation if document is being cancelled
        if self.docstatus == 2:
            return
            
        if not self.gift_given_by:
            self.gift_given_by = frappe.session.user

        if self.customer:
            customer_details = frappe.db.get_value(
                "Loyalty Customer", self.customer, ["mobile_number", "vehicle_number"], as_dict=True
            )
            if customer_details:
                self.customer_mobile = customer_details.mobile_number
                self.vehicle_number = customer_details.vehicle_number

        # The selected warehouse must belong to the selected pump.
        pump_warehouse = frappe.db.get_value("Petrol Pump Location", self.petrol_pump, "warehouse") if self.petrol_pump else None
        if not pump_warehouse or self.warehouse != pump_warehouse:
            frappe.throw(_("The redemption warehouse must match the selected petrol pump's warehouse."))

        # Validate we have items
        if not self.items or len(self.items) == 0:
            frappe.throw(_("Please add at least one gift item"))
        
        # Customer validation
        if self.customer:
            customer = frappe.get_doc("Loyalty Customer", self.customer)
            self.liters_accumulated = customer.current_cycle_liters
            
            # Calculate total points
            total_points = 0
            for item in self.items:
                configured_points = frappe.db.get_value("Pump Gift Item", {
                    "parent": self.petrol_pump, "parenttype": "Petrol Pump Location", "gift_item": item.gift_item
                }, "points_required")
                if configured_points is None:
                    frappe.throw(_("Gift item {0} is not configured for the selected pump.").format(item.gift_item))
                if not configured_points or configured_points <= 0:
                    frappe.throw(_("Configured points must be greater than 0 for {0}").format(item.gift_item))
                # Never trust client-entered points: use the pump's authoritative configuration.
                item.points_required = configured_points
                item.item_name = frappe.db.get_value("Item", item.gift_item, "item_name") or item.gift_item
                total_points += configured_points
                
                # Validate stock for each item
                if self.warehouse and item.gift_item:
                    stock = frappe.db.get_value("Bin", {
                        "item_code": item.gift_item,
                        "warehouse": self.warehouse
                    }, "actual_qty") or 0
                    
                    requested_qty = sum(1 for row in self.items if row.gift_item == item.gift_item)
                    item.available_stock = stock
                    item.stock_after_redeem = stock - requested_qty
                    
                    if stock < requested_qty:
                        frappe.throw(
                            _("Gift item <strong>{0}</strong> is out of stock<br>Available: {1} units").format(
                                item.item_name or item.gift_item, stock
                            )
                        )
            
            self.total_points = total_points
    
    def on_submit(self):
        """Update customer and create stock entry - ALLOW NEGATIVE"""
        if not self.customer or not self.total_points or self.total_points <= 0:
            frappe.throw(_("Customer and items required"))
        
        # Update customer using db_set to avoid validation issues
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        old_points = customer.current_cycle_liters or 0
        
        new_points = old_points - self.total_points
        new_gifts = (customer.total_gifts_received or 0) + len(self.items)
        
        # Direct database update - bypasses validation
        frappe.db.set_value("Loyalty Customer", self.customer, {
            "current_cycle_liters": new_points,
            "total_gifts_received": new_gifts,
            "last_gift_date": frappe.utils.today()
        }, update_modified=True)
        
        # Do not commit inside document lifecycle hooks. Frappe must be able to roll back
        # the customer balance if stock-entry creation or submission fails.
        
        # Create stock entry for all items
        self.create_gift_stock_entry()
        
        # Success message
        new_balance = new_points
        balance_display = f"{new_balance}L" if new_balance >= 0 else f"<span style='color:red;font-weight:bold;'>{new_balance}L (Negative)</span>"
        
        frappe.msgprint(
            _("🎁 {0} gift(s) redeemed successfully!<br><br>Customer: <strong>{1}</strong><br>Previous Points: {2}L<br>New Balance: {3}").format(
                len(self.items), 
                customer.customer_name,
                old_points, 
                balance_display
            ),
            title=_("Redemption Complete"),
            indicator='green'
        )
    
    def on_cancel(self):
        """Reverse redemption - Use direct DB update and reverse stock movement"""
        if self.customer and self.total_points:
            # Get current customer values
            customer = frappe.get_doc("Loyalty Customer", self.customer)
            
            # Calculate new values
            new_points = (customer.current_cycle_liters or 0) + self.total_points
            new_gifts = max(0, (customer.total_gifts_received or 0) - len(self.items))
            
            # Direct database update - bypasses "Cannot Update After Submit"
            frappe.db.set_value("Loyalty Customer", self.customer, {
                "current_cycle_liters": new_points,
                "total_gifts_received": new_gifts
            }, update_modified=False)
            
            frappe.msgprint(
                _("✅ Gift redemption cancelled<br><br>Customer balance restored to: <strong>{0}L</strong>").format(new_points),
                title=_("Cancellation Complete"),
                indicator='blue'
            )

        # Reverse gift stock ledger movements
        from clp.stock import record_gift_stock_movement
        for item in self.items:
            record_gift_stock_movement(
                pump=self.petrol_pump,
                item_code=item.gift_item,
                qty_change=1.0,
                voucher_type="Stock Addition",
                voucher_no=self.name,
                remarks=f"Reversal of Gift Redemption: {self.name}"
            )
        
        # Cancel stock entry if created
        if self.stock_entry:
            try:
                se = frappe.get_doc("Stock Entry", self.stock_entry)
                if se.docstatus == 1:
                    se.cancel()
                    frappe.msgprint(_("Stock entry cancelled"), indicator='blue')
            except Exception as e:
                frappe.log_error(f"Failed to cancel stock entry: {e}", "Gift Redemption Cancel")
    
    def on_trash(self):
        """Prevent deletion if submitted"""
        if self.docstatus == 1:
            frappe.throw(_("Cannot delete submitted Gift Redemption. Please cancel it first."))
    
    def create_gift_stock_entry(self):
        """Create CLP Gift Stock Ledger entry and optional ERPNext stock entry for all gift items"""
        from clp.stock import record_gift_stock_movement
        for item in self.items:
            record_gift_stock_movement(
                pump=self.petrol_pump,
                item_code=item.gift_item,
                qty_change=-1.0,
                voucher_type="Gift Redemption",
                voucher_no=self.name,
                remarks=f"Redeemed by {self.customer_name or self.customer} (Vehicle: {self.vehicle_number or 'N/A'})"
            )

        # Optional ERPNext Stock Entry
        try:
            if frappe.db.exists("DocType", "Stock Entry"):
                stock_items = []
                for item in self.items:
                    stock_items.append({
                        "item_code": item.gift_item,
                        "qty": 1,
                        "s_warehouse": self.warehouse
                    })
                
                se = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Issue",
                    "company": frappe.defaults.get_defaults().get("company"),
                    "posting_date": self.redemption_date or frappe.utils.today(),
                    "remarks": f"Gift Redemption {self.name} - {self.customer} - {len(self.items)} items",
                    "items": stock_items
                })
                se.flags.ignore_permissions = True
                se.insert()
                se.submit()
                self.db_set("stock_entry", se.name, update_modified=False)
        except Exception as e:
            frappe.log_error(f"ERPNext Stock Entry optional creation skipped: {str(e)}", "Gift Redemption")

