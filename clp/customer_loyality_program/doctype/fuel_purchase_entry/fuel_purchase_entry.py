# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FuelPurchaseEntry(Document):
    def validate(self):
        """Validate petrol pump is selected"""
        if not self.petrol_pump:
            frappe.throw(_("Please select Petrol Pump Location"))
        
        if not self.customer:
            frappe.throw(_("Please select Customer"))
        
        if not self.liters or self.liters <= 0:
            frappe.throw(_("Liters must be greater than 0"))
        if self.amount is not None and self.amount < 0:
            frappe.throw(_("Purchase amount cannot be negative"))
    
    def on_submit(self):
        """Apply loyalty balances and referral rewards only for a submitted purchase."""
        self.update_customer_liters()
        self.award_referral_points()
        self.show_customer_status()
    
    def on_cancel(self):
        """Reverse customer liters and any referral reward on cancellation."""
        self.reverse_customer_liters()
        self.reverse_referral_points()
    
    def update_customer_liters(self):
        """Add purchased liters to customer balance after the transaction is submitted."""
        if not self.customer or not self.liters:
            return
        
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        # Null-safe arithmetic protects records created before these fields were initialized.
        customer.total_liters_purchased = (customer.total_liters_purchased or 0) + self.liters
        customer.current_cycle_liters = (customer.current_cycle_liters or 0) + self.liters
        
        customer.flags.ignore_permissions = True
        customer.save()
        frappe.msgprint(
            _("✅ Fuel purchase recorded!<br><br>Customer: <strong>{0}</strong><br>Liters Added: <strong>{1}L</strong><br>New Balance: <strong>{2}L</strong>").format(
                customer.customer_name,
                self.liters,
                customer.current_cycle_liters
            ),
            title=_("Purchase Updated"),
            indicator='green'
        )
    
    def reverse_customer_liters(self):
        """Subtract liters when entry is cancelled"""
        if not self.customer or not self.liters:
            return
        
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        # Reverse the addition
        customer.total_liters_purchased = (customer.total_liters_purchased or 0) - self.liters
        customer.current_cycle_liters = (customer.current_cycle_liters or 0) - self.liters
        
        customer.flags.ignore_permissions = True
        customer.save()
        frappe.msgprint(
            _("Purchase cancelled and customer balance reversed"),
            indicator='blue'
        )
    
    def award_referral_points(self):
        """Create one referral reward for a qualifying, submitted purchase."""
        if not self.customer or not frappe.db.exists("DocType", "CLP Referral Settings"):
            return
        settings = frappe.get_single("CLP Referral Settings")
        if not settings.enabled:
            return
        referrer = frappe.db.get_value("Loyalty Customer", self.customer, "referred_by_customer")
        if not referrer:
            return
        points = int(settings.points_per_eligible_purchase or 0)
        if points <= 0 or (self.amount or 0) < (settings.minimum_purchase_amount or 0):
            return
        # Unique fuel_purchase_entry on Referral Reward Entry makes retries idempotent.
        if frappe.db.exists("Referral Reward Entry", {"fuel_purchase_entry": self.name}):
            return
        reward = frappe.get_doc({
            "doctype": "Referral Reward Entry",
            "referrer": referrer,
            "referred_customer": self.customer,
            "fuel_purchase_entry": self.name,
            "petrol_pump": self.petrol_pump,
            "points_awarded": points,
            "status": "Awarded",
            "reward_date": frappe.utils.now_datetime()
        })
        reward.insert(ignore_permissions=True)
        # Atomic increment prevents concurrent purchases from overwriting each other's rewards.
        frappe.db.sql(
            "UPDATE `tabLoyalty Customer` SET referral_points_balance = COALESCE(referral_points_balance, 0) + %s WHERE name = %s",
            (points, referrer),
        )

    def reverse_referral_points(self):
        """Reverse an awarded referral reward when the fuel entry is cancelled."""
        reward_name = frappe.db.get_value("Referral Reward Entry",
                                          {"fuel_purchase_entry": self.name, "status": "Awarded"}, "name")
        if not reward_name:
            return
        reward = frappe.get_doc("Referral Reward Entry", reward_name)
        # Atomic decrement avoids lost updates if multiple transactions are reversed together.
        frappe.db.sql(
            "UPDATE `tabLoyalty Customer` SET referral_points_balance = GREATEST(0, COALESCE(referral_points_balance, 0) - %s) WHERE name = %s",
            (reward.points_awarded, reward.referrer),
        )
        reward.status = "Reversed"
        reward.reversal_reason = "Fuel purchase cancelled: " + self.name
        reward.save(ignore_permissions=True)

    def show_customer_status(self):
        """Show customer loyalty status after purchase"""
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        frappe.msgprint(
            _("Purchase confirmed for <strong>{0}</strong><br><br>Current Loyalty: <strong>{1}L</strong><br>Total Purchases: <strong>{2}L</strong>").format(
                customer.customer_name,
                customer.current_cycle_liters,
                customer.total_liters_purchased
            ),
            title=_("Customer Status"),
            indicator='blue'
        )
