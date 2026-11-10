import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestPetrolPumpLocation(FrappeTestCase):
    def test_pump_creation_and_fields(self):
        """Test valid petrol pump location creation."""
        pump_name = "_Test Pump Auto"
        if frappe.db.exists("Petrol Pump Location", pump_name):
            frappe.db.delete("Petrol Pump Location", pump_name)

        doc = frappe.get_doc({
            "doctype": "Petrol Pump Location",
            "pump_name": pump_name,
            "is_active": 1
        })
        doc.insert(ignore_permissions=True)
        self.assertEqual(doc.pump_name, pump_name)
        self.assertEqual(doc.is_active, 1)

        # Cleanup
        doc.delete()

