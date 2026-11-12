# Copyright (c) 2025, Aman Boora and contributors
import re
import secrets
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class LoyaltyCustomer(Document):
    def autoname(self):
        if self.get("__qr_code"):
            self.name = self.get("__qr_code")
        else:
            self.name = make_autoname(self.naming_series, doc=self)

    def before_insert(self):
        if not self.created_by_user:
            self.created_by_user = frappe.session.user
        if not self.qr_access_token:
            self.qr_access_token = secrets.token_urlsafe(32)
        if self.referral_points_balance is None:
            self.referral_points_balance = 0

    def validate(self):
        if not self.created_by_user:
            self.created_by_user = frappe.session.user

        if self.vehicle_number:
            if " " in self.vehicle_number:
                frappe.throw(_("Vehicle number must not contain spaces. Please enter in continuous format e.g. MH04GF6292."))
            cleaned_v = self.vehicle_number.strip().upper()
            if not re.match(r"^[A-Z]{2}[0-9]{1,2}[A-Z0-9]{1,3}[0-9]{4}$", cleaned_v):
                frappe.throw(_("Invalid vehicle number format. Please enter a valid registration number (e.g. KA01AB1234)."))
            self.vehicle_number = cleaned_v

        if not self.registration_pump:
            frappe.throw(_("Petrol Pump selection is required for customer registration."))

        self.normalize_customer_fields()
        self.validate_unique_mobile()
        if self.referred_by_customer and self.referred_by_customer == self.name:
            frappe.throw(_("A customer cannot refer themselves."))

    def normalize_customer_fields(self):
        if self.vehicle_number:
            # Vehicle number is deliberately NOT unique; normalize whitespace and case.
            self.vehicle_number = re.sub(r"\s+", "", self.vehicle_number).upper()
        if self.mobile_number:
            self.mobile_number = re.sub(r"\s+", "", self.mobile_number)

    def validate_unique_mobile(self):
        if self.mobile_number:
            exists = frappe.db.exists("Loyalty Customer", {
                "mobile_number": self.mobile_number,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(_("Mobile number {0} is already registered with another customer").format(self.mobile_number))
