import frappe
from frappe.model.document import Document

class CLPReferralSettings(Document):
    def validate(self):
        if (self.points_per_eligible_purchase or 0) < 0:
            frappe.throw("Referral points cannot be negative.")
        if (self.minimum_purchase_amount or 0) < 0:
            frappe.throw("Minimum purchase amount cannot be negative.")
