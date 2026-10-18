# Copyright (c) 2026, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class CLPCustomerBalanceAdjustment(Document):
    def validate(self):
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        self.previous_balance = customer.current_cycle_liters or 0.0
        
        if self.adjustment_type in ("Add Points", "Subtract Points"):
            if not self.points or self.points <= 0:
                frappe.throw(_("Points must be greater than 0 for balance adjustment"))
        else:
            self.points = 0.0
            
        if self.adjustment_type == "Add Points":
            self.new_balance = self.previous_balance + self.points
        elif self.adjustment_type == "Subtract Points":
            if self.points > self.previous_balance:
                frappe.throw(_("Cannot subtract {0} points; customer only has {1} points").format(self.points, self.previous_balance))
            self.new_balance = max(0.0, self.previous_balance - self.points)
        else:
            self.new_balance = self.previous_balance

    def before_submit(self):
        user_roles = set(frappe.get_roles())
        if not ({"System Manager", "Pump Owner", "CLM Incharge"} & user_roles):
            frappe.throw(_("Only Pump Owners or System Managers can adjust customer balances"), frappe.PermissionError)

    def on_submit(self):
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        if self.adjustment_type == "Add Points":
            customer.current_cycle_liters = (customer.current_cycle_liters or 0.0) + self.points
            customer.flags.ignore_permissions = True
            customer.save()
            frappe.msgprint(_("✅ Successfully added {0} points to {1}. New balance: {2}").format(
                self.points, customer.customer_name, customer.current_cycle_liters
            ), indicator="green")
        elif self.adjustment_type == "Subtract Points":
            customer.current_cycle_liters = max(0.0, (customer.current_cycle_liters or 0.0) - self.points)
            customer.flags.ignore_permissions = True
            customer.save()
            frappe.msgprint(_("✅ Successfully deducted {0} points from {1}. New balance: {2}").format(
                self.points, customer.customer_name, customer.current_cycle_liters
            ), indicator="orange")
        
        if self.notes:
            customer.add_comment("Comment", f"Adjustment [{self.name} - {self.adjustment_type}]: {self.notes} (Reason: {self.reason})")

    def on_cancel(self):
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        if self.adjustment_type == "Add Points":
            customer.current_cycle_liters = max(0.0, (customer.current_cycle_liters or 0.0) - self.points)
            customer.flags.ignore_permissions = True
            customer.save()
            frappe.msgprint(_("Reversed addition of {0} points from {1}").format(self.points, customer.customer_name), indicator="blue")
        elif self.adjustment_type == "Subtract Points":
            customer.current_cycle_liters = (customer.current_cycle_liters or 0.0) + self.points
            customer.flags.ignore_permissions = True
            customer.save()
            frappe.msgprint(_("Restored {0} points to {1}").format(self.points, customer.customer_name), indicator="blue")
