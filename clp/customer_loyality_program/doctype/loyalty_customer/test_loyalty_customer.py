import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestLoyaltyCustomer(FrappeTestCase):
    def setUp(self):
        # Create test pump if not exists
        if not frappe.db.exists("Petrol Pump Location", "_Test CLP Pump"):
            pump = frappe.get_doc({
                "doctype": "Petrol Pump Location",
                "pump_name": "_Test CLP Pump"
            })
            pump.insert(ignore_permissions=True)

    def test_vehicle_number_with_spaces_rejected(self):
        """Reject vehicle number containing spaces."""
        customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Space Test",
            "mobile_number": "9999000001",
            "vehicle_number": "MH 04 AB 1234",
            "registration_pump": "_Test CLP Pump"
        })
        with self.assertRaises(ValidationError):
            customer.insert()

    def test_mandatory_registration_pump_on_new_customer(self):
        """Require registration pump for new customer creation."""
        customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "No Pump Test",
            "mobile_number": "9999000002",
            "vehicle_number": "MH04AB1235"
        })
        with self.assertRaises(ValidationError):
            customer.insert()

    def test_valid_customer_creation_and_token(self):
        """Valid customer gets uppercase vehicle, sanitized mobile, and secure QR token."""
        mobile = "9999000003"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": mobile})

        customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Valid Test Customer",
            "mobile_number": mobile,
            "vehicle_number": "mh04gf6292",
            "registration_pump": "_Test CLP Pump"
        })
        customer.insert()

        self.assertEqual(customer.vehicle_number, "MH04GF6292")
        self.assertIsNotNone(customer.qr_access_token)
        self.assertGreaterEqual(len(customer.qr_access_token), 30)

        # Cleanup
        customer.delete()

    def test_unique_mobile_validation(self):
        """Reject duplicate mobile numbers across customers."""
        mobile = "9999000004"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": mobile})

        cust1 = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Customer One",
            "mobile_number": mobile,
            "vehicle_number": "MH04AA1111",
            "registration_pump": "_Test CLP Pump"
        }).insert()

        cust2 = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Customer Two",
            "mobile_number": mobile,
            "vehicle_number": "MH04BB2222",
            "registration_pump": "_Test CLP Pump"
        })

        with self.assertRaises(ValidationError):
            cust2.insert()

        cust1.delete()

    def test_self_referral_rejected(self):
        """Customer cannot refer themselves."""
        mobile = "9999000005"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": mobile})

        cust = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "Referral Test",
            "mobile_number": mobile,
            "vehicle_number": "MH04CC3333",
            "registration_pump": "_Test CLP Pump"
        }).insert()

        cust.referred_by_customer = cust.name
        with self.assertRaises(ValidationError):
            cust.save()

        cust.delete()

