import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestFuelPurchaseEntry(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Petrol Pump Location", "_Test CLP Pump FPE"):
            pump = frappe.get_doc({
                "doctype": "Petrol Pump Location",
                "pump_name": "_Test CLP Pump FPE"
            })
            pump.insert(ignore_permissions=True)

        self.mobile = "9999000010"
        if frappe.db.exists("Loyalty Customer", {"mobile_number": self.mobile}):
            frappe.db.delete("Loyalty Customer", {"mobile_number": self.mobile})

        self.customer = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": "FPE Test Customer",
            "mobile_number": self.mobile,
            "vehicle_number": "MH04FP1001",
            "registration_pump": "_Test CLP Pump FPE"
        }).insert(ignore_permissions=True)

    def tearDown(self):
        if frappe.db.exists("Loyalty Customer", self.customer.name):
            frappe.db.delete("Loyalty Customer", self.customer.name)

    def test_fuel_purchase_submission_updates_points(self):
        """Fuel purchase submission increments current_cycle_liters and total_liters_purchased."""
        entry = frappe.get_doc({
            "doctype": "Fuel Purchase Entry",
            "petrol_pump": "_Test CLP Pump FPE",
            "customer": self.customer.name,
            "liters": 45.5,
            "purchase_date": frappe.utils.now_datetime()
        })
        entry.insert()
        entry.submit()

        updated_cust = frappe.get_doc("Loyalty Customer", self.customer.name)
        self.assertEqual(float(updated_cust.current_cycle_liters), 45.5)
        self.assertEqual(float(updated_cust.total_liters_purchased), 45.5)

        # Cancel entry should reverse customer liters
        entry.cancel()
        reverted_cust = frappe.get_doc("Loyalty Customer", self.customer.name)
        self.assertEqual(float(reverted_cust.current_cycle_liters), 0.0)
        self.assertEqual(float(reverted_cust.total_liters_purchased), 0.0)

    def test_invalid_fuel_entry_rejected(self):
        """Reject fuel purchase entries with 0 or negative liters."""
        entry = frappe.get_doc({
            "doctype": "Fuel Purchase Entry",
            "petrol_pump": "_Test CLP Pump FPE",
            "customer": self.customer.name,
            "liters": 0,
            "purchase_date": frappe.utils.now_datetime()
        })
        with self.assertRaises(ValidationError):
            entry.insert()

