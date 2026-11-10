# CLP Customer Loyalty Program – Master Application Link & Endpoint Directory

**Target Production Domain:** `https://clp.hiideals.com`  
**Base Commit:** `0f66021` | **Audit Branch:** `feat/final-audit-verification`  
**Date:** November 10, 2026  

---

## 1. Requirement-Wise Links Directory (All 16 Requirements)

| Req # | Requirement Name | Web Application Link | API Endpoint | Mobile Application Screen | Verification Evidence | Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **1** | Customer Transaction History | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.check_loyalty_points` | Customer Profile & History Screen | Token URL query parsing & masked lookup | **WORKING** |
| **2** | Pump-Wise Customer Registration | `https://clp.hiideals.com/app/loyalty-customer/new` | `/api/method/frappe.client.insert` | New Customer Registration Screen | Mandatory `registration_pump` validation | **WORKING** |
| **3** | Owner-Only Stock Operations | `https://clp.hiideals.com/app/clp-gift-stock-ledger` | `/api/method/clp.api.adjust_gift_stock` | Manager Stock Adjustment Screen | Role check (`Pump Owner` / `System Manager`) | **WORKING** |
| **4** | User Point Adjustments & Notes | `https://clp.hiideals.com/app/clp-customer-balance-adjustment/new` | `/api/method/frappe.client.insert` | Customer Detail → Adjust Points Action | Add, Subtract, Note Only submittable doc | **WORKING** |
| **5** | Staff Account Creation | `https://clp.hiideals.com/app/user/new` | `/api/method/clp.api.create_staff_account` | Staff Management Tab | Owner RPC creates user & pump settings | **WORKING** |
| **6** | Staff Account Deactivation | `https://clp.hiideals.com/app/user` | `/api/method/clp.api.deactivate_staff_account` | Staff Management List Action | Disables user & deactivates pump settings | **WORKING** |
| **7** | Vehicle Registration Validation | `https://clp.hiideals.com/app/loyalty-customer/new` | `/api/method/frappe.client.insert` | Customer Registration Screen | Rejects vehicle numbers with spaces | **WORKING** |
| **8** | Vehicle Number Search Validation | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.check_loyalty_points` | Customer Search / Lookup | Rejects spaces with continuous format message | **WORKING** |
| **9** | Unique Mobile & Multi-Vehicle | `https://clp.hiideals.com/app/loyalty-customer` | `/api/method/frappe.client.insert` | Customer Registration Screen | Unique mobile validation, vehicle allowed | **WORKING** |
| **10** | Remove Fuel Type & Amount Fields | `https://clp.hiideals.com/app/fuel-purchase-entry/new` | `/api/method/frappe.client.insert` | Fuel Purchase Entry Screen | Fields hidden from attendant screen | **WORKING** |
| **11** | Fuel Entry Quick-Submit Workflow | `https://clp.hiideals.com/app/fuel-purchase-entry/new` | `/api/method/frappe.client.insert` | Attendant Quick Refuel Screen | Bottom save button, anti-double click spinner | **WORKING** |
| **12** | Registration Date Analytics | `https://clp.hiideals.com/app/query-report/Customer%20Registration%20Time%20Analysis` | `/api/method/frappe.desk.query_report.run` | Analytics & Reports Tab | Date filters & hourly/monthly breakdown | **WORKING** |
| **13** | Detailed Reporting Suite | `https://clp.hiideals.com/app/clp` (Reports Section) | `/api/method/frappe.desk.query_report.run` | Reports Viewer Screen | 10 custom reports with export support | **WORKING** |
| **14** | Public QR Information Portal | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.check_loyalty_points` | Public Webview Screen | Catalog, schemes, pump locations | **WORKING** |
| **15** | CLP Activity Audit Log | `https://clp.hiideals.com/app/clp-activity-log` | `/api/method/frappe.client.get_list` | Owner Audit Viewer Screen | Immutable log with before/after state | **WORKING** |
| **16** | Gift Stock & Issuance History | `https://clp.hiideals.com/app/query-report/Gift%20Item%20Stock%20Ledger%20Report` | `/api/method/frappe.desk.query_report.run` | Gift Stock History Screen | Recipient details & added vs issued split | **WORKING** |

---

## 2. Desk Navigation Directory

| Navigation Target | Web URL | Role Access Required | Status |
| :--- | :--- | :--- | :---: |
| **System Login** | `https://clp.hiideals.com/login` | Public | **WORKING** |
| **CLP Desk Workspace** | `https://clp.hiideals.com/app/clp` | All CLP Staff Roles | **WORKING** |
| **Customer List** | `https://clp.hiideals.com/app/loyalty-customer` | CLP Staff | **WORKING** |
| **New Customer Registration** | `https://clp.hiideals.com/app/loyalty-customer/new` | CLP Staff | **WORKING** |
| **Fuel Purchase Entry List** | `https://clp.hiideals.com/app/fuel-purchase-entry` | CLP Staff | **WORKING** |
| **New Fuel Purchase Entry** | `https://clp.hiideals.com/app/fuel-purchase-entry/new` | CLP Staff | **WORKING** |
| **Gift Redemption List** | `https://clp.hiideals.com/app/gift-redemption` | CLP Staff | **WORKING** |
| **New Gift Redemption** | `https://clp.hiideals.com/app/gift-redemption/new` | CLP Staff | **WORKING** |
| **Gift Stock Request (Transfer)** | `https://clp.hiideals.com/app/gift-stock-request` | Pump Manager, Pump Owner | **WORKING** |
| **Petrol Pump Locations** | `https://clp.hiideals.com/app/petrol-pump-location` | Pump Owner, System Manager | **WORKING** |
| **Balance Adjustments** | `https://clp.hiideals.com/app/clp-customer-balance-adjustment` | Pump Owner, System Manager | **WORKING** |
| **Gift Stock Ledger** | `https://clp.hiideals.com/app/clp-gift-stock-ledger` | CLP Staff | **WORKING** |
| **Activity Logs** | `https://clp.hiideals.com/app/clp-activity-log` | Pump Owner, System Manager | **WORKING** |
| **User Pump Settings** | `https://clp.hiideals.com/app/user-pump-settings` | Pump Owner, System Manager | **WORKING** |
| **User Management** | `https://clp.hiideals.com/app/user` | System Manager | **WORKING** |
| **Customer Portal Link** | `https://clp.hiideals.com/loyality/check` | Public / Customer Guest | **WORKING** |
| **Redirect Route Alias** | `https://clp.hiideals.com/loyalty/check` | Public / Customer Guest | **WORKING** |

---

## 3. Whitelisted API Endpoints

### 1. `clp.api.check_loyalty_points`
- **Method:** `GET` / `POST`
- **Auth:** Public (`allow_guest=True`)
- **Rate Limit:** 30 requests / 60 seconds
- **Parameters:** `vehicle` (str), `mobile` (str), `token` (str)
- **Response:**
  ```json
  {
    "message": {
      "found": true,
      "customer": {
        "name": "MANUAL-0001",
        "customer_name": "Rahul S.***",
        "vehicle_number": "MH04GF6292",
        "mobile_number": "******6292",
        "current_cycle_liters": 45.0,
        "total_liters_purchased": 150.0,
        "total_gifts_received": 2
      },
      "purchases": [],
      "redemptions": []
    }
  }
  ```

### 2. `clp.api.scan_and_process_qr`
- **Method:** `POST`
- **Auth:** CLP Staff Role Required
- **Parameters:** `qr_data` (string - URL with token, legacy id, raw token, or customer ID)
- **Response:**
  ```json
  {
    "message": {
      "exists": true,
      "customer_id": "MANUAL-0001",
      "customer_name": "Rahul Sharma",
      "vehicle_number": "MH04GF6292",
      "mobile_number": "9820123456",
      "current_cycle_liters": 45.0
    }
  }
  ```

### 3. `clp.api.get_whatsapp_link`
- **Method:** `GET` / `POST`
- **Auth:** CLP Staff Role Required
- **Parameters:** `customer_id` (str), `pump_name` (optional str)
- **Response:**
  ```json
  {
    "message": {
      "url": "https://wa.me/919820123456?text=...",
      "phone": "919820123456",
      "customer_name": "Rahul Sharma"
    }
  }
  ```

### 4. `clp.api.create_staff_account`
- **Method:** `POST`
- **Auth:** Owner-Only (`Pump Owner` / `System Manager`)
- **Parameters:** `email` (str), `first_name` (str), `last_name` (optional str), `mobile_no` (optional str), `pump` (str), `role` (str)
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "user": "staff1@hiideals.com",
      "role": "CLM Incharge",
      "pump": "Main Pump Station",
      "is_new": true
    }
  }
  ```

### 5. `clp.api.deactivate_staff_account`
- **Method:** `POST`
- **Auth:** Owner-Only (`Pump Owner` / `System Manager`)
- **Parameters:** `user_id` (str)
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "message": "Staff account staff1@hiideals.com has been deactivated."
    }
  }
  ```

### 6. `clp.api.adjust_gift_stock`
- **Method:** `POST`
- **Auth:** Owner-Only (`Pump Owner` / `System Manager`)
- **Parameters:** `item_code` (str), `warehouse` (str), `qty` (float), `action` ("add" | "remove"), `reason` (str)
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "item_code": "GIFT-WATCH-01",
      "actual_qty": 25.0
    }
  }
  ```

---

## 4. Report Direct URLs

| Report Name | Direct Production URL | Permitted Roles | Status |
| :--- | :--- | :--- | :---: |
| **Customer Loyalty Summary** | `https://clp.hiideals.com/app/query-report/Customer%20Loyalty%20Summary` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Customer Registration Time Analysis** | `https://clp.hiideals.com/app/query-report/Customer%20Registration%20Time%20Analysis` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Daily Pump Sales Summary** | `https://clp.hiideals.com/app/query-report/Daily%20Pump%20Sales%20Summary` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Gift Item Stock Ledger Report** | `https://clp.hiideals.com/app/query-report/Gift%20Item%20Stock%20Ledger%20Report` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Gift Redemption Summary** | `https://clp.hiideals.com/app/query-report/Gift%20Redemption%20Summary` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Inactive Customers Report** | `https://clp.hiideals.com/app/query-report/Inactive%20Customers%20Report` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Pump Wise Gift Stock** | `https://clp.hiideals.com/app/query-report/Pump%20Wise%20Gift%20Stock` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **Referral Rewards Report** | `https://clp.hiideals.com/app/query-report/Referral%20Rewards%20Report` | CLP Referral Manager, Pump Owner, System Manager | **WORKING** |
| **Registration Time Report** | `https://clp.hiideals.com/app/query-report/Registration%20Time%20Report` | CLP Reports Viewer, Pump Owner, System Manager | **WORKING** |
| **CLP Activity Audit Report** | `https://clp.hiideals.com/app/query-report/CLP%20Activity%20Audit%20Report` | Pump Owner, System Manager | **WORKING** |

---

## 5. Mobile Application Distribution

- **APK Name:** `CLP_Mobile_App_Fixed_v1.1.apk`
- **Location on Host:** `E:\clp updated code\clp-mobile-app\CLP_Mobile_App_Fixed_v1.1.apk`
- **File Size:** 85.81 MB (85,810,937 bytes)
- **App Version:** 1.1.0
- **Package ID:** `com.hiideals.clp`
- **Configured Production API Base:** `https://clp.hiideals.com`
- **Main App Icon:** `assets/images/clp-app-icon.png` (Official CLP Branding)
