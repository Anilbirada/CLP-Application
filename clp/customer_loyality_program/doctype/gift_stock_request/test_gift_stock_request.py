import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestGiftStockRequest(FrappeTestCase):
    def test_zero_or_negative_quantity_rejected(self):
        """Reject stock request with zero or negative quantity."""
        req = frappe.get_doc({
            "doctype": "Gift Stock Request",
            "quantity": 0,
            "source_warehouse": "W1",
            "requesting_warehouse": "W2"
        })
        with self.assertRaises(ValidationError):
            req.validate()

    def test_same_source_and_destination_rejected(self):
        """Reject stock request when source and destination warehouse are identical."""
        req = frappe.get_doc({
            "doctype": "Gift Stock Request",
            "quantity": 5,
            "source_warehouse": "W1",
            "requesting_warehouse": "W1"
        })
        with self.assertRaises(ValidationError):
            req.validate()

    def test_missing_warehouse_rejected(self):
        """Reject stock request without source or destination warehouse."""
        req = frappe.get_doc({
            "doctype": "Gift Stock Request",
            "quantity": 5,
            "source_warehouse": None,
            "requesting_warehouse": "W2"
        })
        with self.assertRaises(ValidationError):
            req.validate()

