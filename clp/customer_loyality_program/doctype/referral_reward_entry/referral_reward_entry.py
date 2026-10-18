# Referral rewards ledger. Records one reward per eligible fuel purchase.
import frappe
from frappe.model.document import Document

class ReferralRewardEntry(Document):
    def validate(self):
        if self.points_awarded is None or self.points_awarded <= 0:
            frappe.throw("Referral points must be greater than zero.")
        if self.referrer == self.referred_customer:
            frappe.throw("A customer cannot refer themselves.")
