import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestGiftRedemption(FrappeTestCase):
    def setUp(self):
        # Create test pump if not exists
        if not frappe.db.exists("Petrol Pump Location", "_Test CLP Pump GR"):
            pump = frappe.get_doc({
                "doctype": "Petrol Pump Location",
                "pump_name": "_Test CLP Pump GR"
            })
            pump.insert(ignore_permissions=True)

        self.mobile = "9999000020"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": self.mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": self.mobile})

        self.customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "GR Test Customer",
            "mobile_number": self.mobile,
            "vehicle_number": "MH04GR2001",
            "registration_pump": "_Test CLP Pump GR"
        }).insert(ignore_permissions=True)

    def tearDown(self):
        if frappe.db.exists("Loyalty Customer", self.customer.name):
            frappe.db.delete("Loyalty Customer", self.customer.name)

    def test_empty_items_rejected(self):
        """Redemption without gift items must be rejected."""
        redemption = frappe.get_doc({
            "doctype": "Gift Redemption",
            "customer": self.customer.name,
            "petrol_pump": "_Test CLP Pump GR",
            "items": []
        })
        with self.assertRaises(ValidationError):
            redemption.insert()

    def test_warehouse_mismatch_rejected(self):
        """Redemption warehouse must match petrol pump warehouse."""
        redemption = frappe.get_doc({
            "doctype": "Gift Redemption",
            "customer": self.customer.name,
            "petrol_pump": "_Test CLP Pump GR",
            "warehouse": "_Invalid Warehouse",
            "items": []
        })
        with self.assertRaises(ValidationError):
            redemption.insert()

    def test_customer_pii_snapshotted(self):
        """Customer mobile and vehicle number are snapshotted on insertion."""
        redemption = frappe.new_doc("Gift Redemption")
        redemption.customer = self.customer.name
        redemption.before_insert()
        self.assertEqual(redemption.customer_mobile, self.customer.mobile_number)
        self.assertEqual(redemption.vehicle_number, self.customer.vehicle_number)
        self.assertEqual(redemption.customer_name, self.customer.customer_name)

