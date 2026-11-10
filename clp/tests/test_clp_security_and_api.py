# Copyright (c) 2026, Aman Boora and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from clp.api import check_loyalty_points, scan_and_process_qr

class TestCLPSecurityAndAPI(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Petrol Pump Location", "_Test Security Pump"):
            pump = frappe.get_doc({
                "doctype": "Petrol Pump Location",
                "pump_name": "_Test Security Pump"
            })
            pump.insert(ignore_permissions=True)

        self.mobile = "9876543210"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": self.mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": self.mobile})

        self.customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Suresh Kumar",
            "mobile_number": self.mobile,
            "vehicle_number": "DL01AB9999",
            "registration_pump": "_Test Security Pump"
        }).insert(ignore_permissions=True)

    def tearDown(self):
        if frappe.db.exists("Loyalty Customer", self.customer.name):
            frappe.db.delete("Loyalty Customer", self.customer.name)

    def test_guest_mobile_masking_in_check_loyalty_points(self):
        """Guests querying points must see masked mobile number and name."""
        frappe.set_user("Guest")
        res = check_loyalty_points(mobile=self.mobile)
        self.assertTrue(res.get("found"))
        cust = res.get("customer")
        self.assertEqual(cust.get("mobile_number"), "******3210")
        self.assertIn("***", cust.get("customer_name"))
        frappe.set_user("Administrator")

    def test_authorized_token_access_in_check_loyalty_points(self):
        """Accessing points with valid token returns unmasked profile to customer."""
        frappe.set_user("Guest")
        res = check_loyalty_points(token=self.customer.qr_access_token)
        self.assertTrue(res.get("found"))
        cust = res.get("customer")
        self.assertEqual(cust.get("mobile_number"), self.mobile)
        self.assertEqual(cust.get("customer_name"), "Suresh Kumar")
        frappe.set_user("Administrator")

    def test_qr_scanner_parses_tokenized_urls(self):
        """Staff QR scanner resolves customer from full portal URL with ?token=..."""
        frappe.set_user("Administrator")
        qr_url = f"https://clp.hiideals.com/loyality/check?token={self.customer.qr_access_token}"
        res = scan_and_process_qr(qr_url)
        self.assertTrue(res.get("exists"))
        self.assertEqual(res.get("customer_id"), self.customer.name)
