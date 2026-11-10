# CLP Customer Loyalty Program – API Test Results (Final Acceptance)

**Target Domain:** `https://clp.hiideals.com`  
**Current Git Commit:** `f31e08c` | **Branch:** `main`  
**Base Commit:** `e5acab4`  
**API Specification:** Frappe Whitelisted RPC Directory  
**Audit Team:** Senior QA Automation & Acceptance Engineering Team  
**Date:** November 10, 2026  

---

## 1. Whitelisted API Endpoints Directory & Test Summary

All whitelisted methods in `clp/api.py` were audited for parameter validation, role permission checks, response structures, and database persistence.

| Endpoint Method Name | HTTP Method | Auth Required | Authorized Roles | Response Schema | Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `clp.api.check_loyalty_points` | `GET`/`POST` | No (Guest) | Any / Guest | `dict` (found, customer, purchases, redemptions) | **PASS** |
| `clp.api.scan_and_process_qr` | `POST` | Yes | Attendant Roles | `dict` (exists, customer_id, customer) | **PASS** |
| `clp.api.generate_qr_image` | `POST` | Yes | Staff Roles | `dict` (image base64) | **PASS** |
| `clp.api.bulk_generate_qr_codes` | `POST` | Yes | System Manager | `dict` / `file` (ZIP) | **PASS** |
| `clp.api.adjust_gift_stock` | `POST` | Yes | System Manager, Pump Owner | `dict` (success, balance) | **PASS** |
| `clp.api.get_gift_stock_data` | `GET` | Yes | Staff Roles | `list` of gift stock records | **PASS** |
| `clp.api.create_staff_account` | `POST` | Yes | System Manager, Pump Owner | `dict` (success, user, role, pump) | **PASS** |
| `clp.api.deactivate_staff_account` | `POST` | Yes | System Manager, Pump Owner | `dict` (success, message) | **PASS** |
| `clp.api.get_staff_list` | `GET` | Yes | System Manager, Pump Owner | `list` of staff members | **PASS** |
| `clp.api.update_profile_photo` | `POST` | Yes | Any Authenticated User / Owner | `dict` (success, user, user_image) | **PASS** |
| `clp.api.search_customer_for_scanner`| `GET`/`POST`| Yes | Staff Roles | `list` of customer records | **PASS** |
| `clp.api.get_user_default_pump` | `GET` | Yes | Authenticated Users | `dict` (default_pump, warehouse) | **PASS** |
| `clp.api.set_my_pump_settings` | `POST` | Yes | Authenticated Users | `dict` (success) | **PASS** |
| `clp.api.get_available_gifts` | `GET` | Yes | Staff Roles | `list` of available gifts | **PASS** |
| `clp.api.get_whatsapp_link` | `GET` | Yes | Staff Roles | `dict` (whatsapp_url, message) | **PASS** |
| `clp.api.update_customer_profile` | `POST` | Yes | Token Auth / Staff | `dict` (success, customer) | **PASS** |

---

## 2. In-Depth Endpoint Test Cases

### 1. `clp.api.check_loyalty_points`
- **Route:** `/api/method/clp.api.check_loyalty_points`
- **Parameters:** `vehicle` (optional), `mobile` (optional), `token` (optional)
- **Test Scenarios:**
  - *TC-API-01 (Valid continuous vehicle):* `vehicle="MH04GF6292"` -> Returns customer summary, recent purchases, and redemptions. (Result: **PASS**)
  - *TC-API-02 (Vehicle with spaces):* `vehicle="MH 04 GF 6292"` -> Returns `found: False`, `error: "Vehicle number must not contain spaces. Please enter in continuous format e.g. MH04GF6292."`. (Result: **PASS**)
  - *TC-API-03 (Guest query masking):* Queried as Guest by phone -> `mobile_number` returns masked (`******3210`) and `customer_name` returns masked (`Ramesh S***`). (Result: **PASS**)
  - *TC-API-04 (Token authorized query):* Queried with authentic `token` -> Returns unmasked mobile number and customer name. (Result: **PASS**)

---

### 2. `clp.api.adjust_gift_stock`
- **Route:** `/api/method/clp.api.adjust_gift_stock`
- **Parameters:** `item_code`, `warehouse`, `qty`, `action` (`"add"` or `"remove"`), `reason`
- **Test Scenarios:**
  - *TC-API-05 (Owner authorization):* Called as `Pump Owner` -> Successfully posts stock movement. (Result: **PASS**)
  - *TC-API-06 (Unauthorized attendant):* Called as `CLM Incharge` -> Throws `PermissionError: Only Pump Owners and System Managers are authorized to adjust gift stock.`. (Result: **PASS**)
  - *TC-API-07 (Negative stock prevention):* Attempting to remove 50 units when only 10 exist at warehouse -> Throws `ValidationError: Cannot remove 50 units; available stock at pump is only 10 units.`. (Result: **PASS**)
  - *TC-API-08 (Missing reason):* Missing reason parameter -> Throws `ValidationError: A reason is required for stock adjustment.`. (Result: **PASS**)

---

### 3. `clp.api.create_staff_account` & `deactivate_staff_account`
- **Route:** `/api/method/clp.api.create_staff_account`
- **Parameters:** `email`, `first_name`, `last_name`, `mobile_no`, `pump`, `role`
- **Test Scenarios:**
  - *TC-API-09 (Create staff by Owner):* Owner provisions `staff@highway.com` with role `CLM Incharge` and pump `Main Pump Station` -> User created with enabled status and default pump configured. (Result: **PASS**)
  - *TC-API-10 (Unauthorized creation):* Called by non-owner -> HTTP 403 `PermissionError`. (Result: **PASS**)
  - *TC-API-11 (Deactivate staff):* Calls `deactivate_staff_account` -> Sets `enabled = 0`, disables login, retains historical fuel entries. (Result: **PASS**)
  - *TC-API-12 (Self-deactivation guard):* Owner attempting to deactivate their own account -> Throws `You cannot deactivate your own account.`. (Result: **PASS**)

---

### 4. `clp.api.update_profile_photo`
- **Route:** `/api/method/clp.api.update_profile_photo`
- **Parameters:** `photo_url`, `user` (optional, defaults to session user)
- **Test Scenarios:**
  - *TC-API-13 (Self photo update):* User uploads new avatar image -> Updates `tabUser.user_image` and clears cache. (Result: **PASS**)
  - *TC-API-14 (Admin updating user photo):* System Manager updates another user's photo -> Allowed. (Result: **PASS**)
  - *TC-API-15 (Unauthorized user cross-update):* Attendant attempting to change Administrator's photo -> Throws `PermissionError`. (Result: **PASS**)

---

## 3. API Robustness & Error Handling Matrix

| Vulnerability / Stress Vector | Mitigation Tested | Outcome |
| :--- | :--- | :---: |
| **SQL Injection** | Parameterized queries with `%s` and `%(param)s` dictionaries | Safe – No Injection |
| **ID Enumeration (PII Scraping)** | Phone numbers and names masked for unauthenticated callers | Safe – Data Protected |
| **Negative Inventory Injection** | Pre-flight stock availability check on all removal RPCs | Safe – Negative Prevented |
| **Session Hijacking** | Frappe native CSRF token validation and session cookie signing | Safe – Protected |
| **Malformed JSON Payload** | Strict type casting (`float(qty)`, string stripping, null checks) | Handled Gracefully |
