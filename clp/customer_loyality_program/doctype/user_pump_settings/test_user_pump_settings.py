import frappe
from frappe.tests.utils import FrappeTestCase

class TestUserPumpSettings(FrappeTestCase):
    def setUp(self):
        pump_name = "_Test Pump Settings Auto"
        if not frappe.db.exists("Petrol Pump Location", pump_name):
            pump = frappe.get_doc({
                "doctype": "Petrol Pump Location",
                "pump_name": pump_name,
                "is_active": 1
            })
            pump.insert(ignore_permissions=True)

    def test_user_pump_settings_creation(self):
        """Test assigning default pump to user in User Pump Settings."""
        user = "test_attendant@example.com"
        pump_name = "_Test Pump Settings Auto"

        if frappe.db.exists("User Pump Settings", user):
            frappe.db.delete("User Pump Settings", user)

        settings = frappe.get_doc({
            "doctype": "User Pump Settings",
            "user": user,
            "default_pump": pump_name,
            "is_active": 1
        })
        settings.insert(ignore_permissions=True)

        self.assertEqual(settings.user, user)
        self.assertEqual(settings.default_pump, pump_name)
        self.assertEqual(settings.is_active, 1)

        # Cleanup
        settings.delete()

