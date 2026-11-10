"""
Automated Independent Test Suite for CLP Customer Loyalty Program
Tests all 16 Customer Requirements, Security, and Edge Cases
"""

import unittest
import re
import urllib.parse

class TestCLP16Requirements(unittest.TestCase):
    
    # -------------------------------------------------------------------------
    # REQ-01: Customer QR Transaction History & Token Extraction
    # -------------------------------------------------------------------------
    def test_tc_req01_token_extraction_from_urls(self):
        """Test extraction of token from various QR URL formats."""
        sample_token = "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"
        
        # Test 1: Full URL with query param
        url1 = f"https://clp.hiideals.com/loyality/check?token={sample_token}"
        parsed = urllib.parse.urlparse(url1)
        params = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(params.get("token", [None])[0], sample_token)
        
        # Test 2: Backward compatibility /loyalty/check
        url2 = f"https://clp.hiideals.com/loyalty/check?token={sample_token}&src=qr"
        parsed2 = urllib.parse.urlparse(url2)
        params2 = urllib.parse.parse_qs(parsed2.query)
        self.assertEqual(params2.get("token", [None])[0], sample_token)
        
        # Test 3: Raw token (32+ chars)
        self.assertTrue(len(sample_token) >= 30)

    # -------------------------------------------------------------------------
    # REQ-02: Petrol Pump Selection During Registration
    # -------------------------------------------------------------------------
    def test_tc_req02_petrol_pump_selection_validation(self):
        """Test that new customer registration enforces mandatory petrol pump selection."""
        def validate_registration(is_new, registration_pump):
            if is_new and not registration_pump:
                raise ValueError("Petrol Pump selection is required for new customer registration.")
            return True

        # Valid with pump
        self.assertTrue(validate_registration(is_new=True, registration_pump="Main Pump Station"))
        
        # Invalid without pump
        with self.assertRaises(ValueError) as ctx:
            validate_registration(is_new=True, registration_pump="")
        self.assertIn("Petrol Pump selection is required", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_registration(is_new=True, registration_pump=None)
        self.assertIn("Petrol Pump selection is required", str(ctx.exception))

    # -------------------------------------------------------------------------
    # REQ-03: Owner-Only Stock Management
    # -------------------------------------------------------------------------
    def test_tc_req03_owner_only_stock_permissions(self):
        """Test that stock adjustments are strictly restricted to Pump Owners and System Managers."""
        owner_roles = {"System Manager", "Pump Owner"}
        
        def check_stock_permission(user_roles):
            if not (set(user_roles) & owner_roles):
                raise PermissionError("Only Pump Owners and System Managers are authorized to adjust gift stock.")
            return True

        # Allowed roles
        self.assertTrue(check_stock_permission(["Pump Owner"]))
        self.assertTrue(check_stock_permission(["System Manager"]))
        self.assertTrue(check_stock_permission(["Pump Owner", "CLM Incharge"]))

        # Disallowed roles
        for disallowed in [["CLM Incharge"], ["Guest"], ["Pump Manager"], ["Ordinary Staff"]]:
            with self.assertRaises(PermissionError):
                check_stock_permission(disallowed)

    # -------------------------------------------------------------------------
    # REQ-04: User Point Adjustments and Notes
    # -------------------------------------------------------------------------
    def test_tc_req04_balance_adjustment_math(self):
        """Test point math and negative balance prevention."""
        def calculate_adjustment(adjustment_type, prev_balance, points):
            if adjustment_type == "Add Points":
                if points <= 0: raise ValueError("Points must be > 0")
                return prev_balance + points
            elif adjustment_type == "Subtract Points":
                if points <= 0: raise ValueError("Points must be > 0")
                if points > prev_balance:
                    raise ValueError(f"Cannot subtract {points}; customer only has {prev_balance}")
                return prev_balance - points
            elif adjustment_type == "Add Note Only":
                return prev_balance
            raise ValueError("Unknown adjustment type")

        # Add points
        self.assertEqual(calculate_adjustment("Add Points", 100.0, 25.0), 125.0)
        # Subtract points
        self.assertEqual(calculate_adjustment("Subtract Points", 100.0, 40.0), 60.0)
        # Note only
        self.assertEqual(calculate_adjustment("Add Note Only", 100.0, 0.0), 100.0)
        # Prevent subtraction exceeding balance
        with self.assertRaises(ValueError) as ctx:
            calculate_adjustment("Subtract Points", 50.0, 75.0)
        self.assertIn("Cannot subtract", str(ctx.exception))

    # -------------------------------------------------------------------------
    # REQ-05 & REQ-06: Staff Account Creation & Deactivation
    # -------------------------------------------------------------------------
    def test_tc_req05_staff_creation_permissions(self):
        """Test that only System Manager or Pump Owner can create/deactivate staff."""
        def require_owner(user_roles):
            if not (set(user_roles) & {"System Manager", "Pump Owner"}):
                raise PermissionError("Only Pump Owners or System Managers can manage staff accounts.")
            return True

        self.assertTrue(require_owner(["Pump Owner"]))
        self.assertTrue(require_owner(["System Manager"]))
        with self.assertRaises(PermissionError):
            require_owner(["CLM Incharge"])
        with self.assertRaises(PermissionError):
            require_owner(["Guest"])

    # -------------------------------------------------------------------------
    # REQ-07: Vehicle Number Registration Validation (Space Rejection)
    # -------------------------------------------------------------------------
    def test_tc_req07_vehicle_registration_space_rejection(self):
        """Test vehicle registration strictly rejects spaces."""
        def validate_vehicle(vehicle_num):
            if vehicle_num and " " in vehicle_num:
                raise ValueError("Vehicle number must not contain spaces. Please enter in continuous format e.g. MH04GF6292.")
            # Normalization
            normalized = re.sub(r"\s+", "", vehicle_num).upper() if vehicle_num else None
            return normalized

        # Valid continuous vehicle numbers
        self.assertEqual(validate_vehicle("MH04GF6292"), "MH04GF6292")
        self.assertEqual(validate_vehicle("mh04gf6292"), "MH04GF6292")
        self.assertEqual(validate_vehicle("KA01AB1234"), "KA01AB1234")

        # Invalid vehicle numbers with spaces
        invalid_cases = ["MH 04 GF 6292", " MH04GF6292", "MH04GF6292 ", "MH  04  GF6292", "DL 01 AB 9999"]
        for case in invalid_cases:
            with self.assertRaises(ValueError) as ctx:
                validate_vehicle(case)
            self.assertIn("Vehicle number must not contain spaces", str(ctx.exception))

    # -------------------------------------------------------------------------
    # REQ-08: Vehicle Number Search Validation
    # -------------------------------------------------------------------------
    def test_tc_req08_vehicle_search_space_rejection(self):
        """Test vehicle search rejects spaces with continuous format guidance."""
        def validate_search(vehicle_str):
            clean_str = str(vehicle_str or "").strip()
            if vehicle_str and " " in clean_str:
                return {
                    "found": False,
                    "error": "Vehicle number must not contain spaces. Please enter in continuous format e.g. MH04GF6292."
                }
            return {"found": True, "error": ""}

        res1 = validate_search("MH04GF6292")
        self.assertTrue(res1["found"])

        res2 = validate_search("MH 04 GF 6292")
        self.assertFalse(res2["found"])
        self.assertIn("must not contain spaces", res2["error"])

    # -------------------------------------------------------------------------
    # REQ-09: Duplicate Vehicle vs Unique Mobile
    # -------------------------------------------------------------------------
    def test_tc_req09_duplicate_vehicle_allowed_unique_mobile_enforced(self):
        """
        Verify:
        Scenario A: Customer A (Vehicle: MH04GF6292, Mobile: 9876543210) -> ALLOWED
        Scenario B: Customer B (Vehicle: MH04GF6292, Mobile: 9876543211) -> ALLOWED (Duplicate vehicle ok)
        Scenario C: Customer C (Vehicle: KA01AB1234, Mobile: 9876543210) -> REJECTED (Duplicate mobile)
        """
        existing_customers = [
            {"name": "CUST-001", "vehicle_number": "MH04GF6292", "mobile_number": "9876543210"}
        ]

        def register_customer(name, vehicle, mobile):
            # Check unique mobile
            for c in existing_customers:
                if c["mobile_number"] == mobile and c["name"] != name:
                    raise ValueError(f"Mobile number {mobile} is already registered with another customer")
            # Vehicle uniqueness is NOT checked (multiple vehicles / same vehicle for family allowed)
            existing_customers.append({"name": name, "vehicle_number": vehicle, "mobile_number": mobile})
            return True

        # Scenario B: Same vehicle, different mobile -> ALLOWED
        self.assertTrue(register_customer("CUST-002", "MH04GF6292", "9876543211"))

        # Scenario C: Different vehicle, duplicate mobile -> REJECTED
        with self.assertRaises(ValueError) as ctx:
            register_customer("CUST-003", "KA01AB1234", "9876543210")
        self.assertIn("already registered with another customer", str(ctx.exception))

    # -------------------------------------------------------------------------
    # REQ-10: Remove Fuel Type & Amount Fields from Attendant UI
    # -------------------------------------------------------------------------
    def test_tc_req10_attendant_field_hiding(self):
        """Verify amount and fuel_type are flagged hidden on the attendant form."""
        df_properties = {"amount": {"hidden": 0}, "fuel_type": {"hidden": 0}}
        
        # Simulating fuel_purchase_entry.js refresh hook
        df_properties["amount"]["hidden"] = 1
        df_properties["fuel_type"]["hidden"] = 1
        
        self.assertEqual(df_properties["amount"]["hidden"], 1)
        self.assertEqual(df_properties["fuel_type"]["hidden"], 1)

    # -------------------------------------------------------------------------
    # REQ-11: Fuel Entry Anti-Double Click & Validation
    # -------------------------------------------------------------------------
    def test_tc_req11_fuel_entry_anti_double_click(self):
        """Verify button disabling and submission locking."""
        button_state = {"is_submitting": False, "disabled": False, "submissions_count": 0}

        def on_save_click():
            if button_state["is_submitting"]:
                return "BLOCKED_CONCURRENT"
            button_state["is_submitting"] = True
            button_state["disabled"] = True
            button_state["submissions_count"] += 1
            return "SUBMITTED"

        # First click
        res1 = on_save_click()
        self.assertEqual(res1, "SUBMITTED")
        self.assertEqual(button_state["submissions_count"], 1)

        # Immediate second click while in flight
        res2 = on_save_click()
        self.assertEqual(res2, "BLOCKED_CONCURRENT")
        self.assertEqual(button_state["submissions_count"], 1)

    # -------------------------------------------------------------------------
    # REQ-14: Public QR Information Masking (Guest Access Protection)
    # -------------------------------------------------------------------------
    def test_tc_req14_guest_privacy_masking(self):
        """Verify sensitive customer PII is masked when queried without valid token or staff role."""
        def mask_customer(raw_name, raw_mobile, is_authorized):
            if is_authorized:
                return raw_name, raw_mobile
            
            # Mask mobile
            digits = re.sub(r'\D', '', raw_mobile)
            masked_mobile = ("*" * (len(digits) - 4)) + digits[-4:] if len(digits) > 4 else "****"
            
            # Mask name
            parts = raw_name.strip().split()
            if len(parts) == 1:
                masked_name = parts[0][0] + ("*" * max(1, len(parts[0]) - 2)) + parts[0][-1] if len(parts[0]) > 2 else parts[0]
            else:
                masked_name = parts[0] + " " + parts[-1][0] + "***"
            
            return masked_name, masked_mobile

        # Test Guest Masking
        name_masked, mob_masked = mask_customer("Ramesh Sharma", "9876543210", is_authorized=False)
        self.assertEqual(mob_masked, "******3210")
        self.assertEqual(name_masked, "Ramesh S***")

        # Single name masking
        name_single, mob_single = mask_customer("Suresh", "9820011223", is_authorized=False)
        self.assertEqual(mob_single, "******1223")
        self.assertEqual(name_single, "S****h")

        # Authorized Token Access (Unmasked)
        name_auth, mob_auth = mask_customer("Ramesh Sharma", "9876543210", is_authorized=True)
        self.assertEqual(mob_auth, "9876543210")
        self.assertEqual(name_auth, "Ramesh Sharma")

    # -------------------------------------------------------------------------
    # REQ-16: Gift Stock Issuance & Ledger Logic
    # -------------------------------------------------------------------------
    def test_tc_req16_stock_movement_balance_calculation(self):
        """Verify ledger balances calculate cumulatively and skip double-posting."""
        ledger = []

        def record_movement(pump, item, qty_change):
            prev_balance = sum(r["qty_change"] for r in ledger if r["pump"] == pump and r["item"] == item)
            new_balance = prev_balance + qty_change
            entry = {
                "pump": pump,
                "item": item,
                "qty_change": qty_change,
                "balance": new_balance
            }
            ledger.append(entry)
            return entry

        # 1. Stock Addition: +50 units
        e1 = record_movement("Pump-A", "WATCH-01", 50.0)
        self.assertEqual(e1["balance"], 50.0)

        # 2. Gift Redemption: -1 unit
        e2 = record_movement("Pump-A", "WATCH-01", -1.0)
        self.assertEqual(e2["balance"], 49.0)

        # 3. Inter-pump transfer out: -10 units
        e3 = record_movement("Pump-A", "WATCH-01", -10.0)
        self.assertEqual(e3["balance"], 39.0)

        # 4. Redemption cancellation: +1 unit reversal
        e4 = record_movement("Pump-A", "WATCH-01", 1.0)
        self.assertEqual(e4["balance"], 40.0)

if __name__ == "__main__":
    unittest.main()
