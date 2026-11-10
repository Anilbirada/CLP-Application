# CLP Customer Loyalty Program – Role-Based Security & Permissions Test Report

**Target Domain:** `https://clp.hiideals.com`  
**Current Git Commit:** `f31e08c` | **Branch:** `main`  
**Base Commit:** `e5acab4`  
**Execution Environment:** Frappe v15 + MariaDB 10.6 + Redis  
**Audit Team:** Senior QA Automation & Acceptance Engineering Team  
**Date:** November 10, 2026  

---

## 1. Role Permission Matrix Overview

The CLP system defines strict Role-Based Access Controls (RBAC) across administrative, managerial, frontline, and public access tiers:

| User Role | Target User Persona | Primary Responsibilities | Administrative Scope |
| :--- | :--- | :--- | :--- |
| **System Manager** | Platform Administrator | Full technical control, schema migrations, system settings | Universal Access |
| **Pump Owner** | Station Owner / Franchisee | Staff provisioning, stock adjustments, financial oversight, reports | All Pump Operations |
| **Pump Manager** | Shift Manager | Daily operations, stock transfer requests, local reports | Station Management |
| **CLM Incharge** | Frontline Pump Attendant | Customer registration, fuel entry, gift issuance | Refuel & Redeem Only |
| **CLP Stock Add** | Inventory Receiver | Stock receiving and initial inventory load | Stock Additions Only |
| **CLP Stock Subtract**| Inventory Auditor | Damaged/expired gift removal | Stock Deductions Only |
| **CLP Stock Transfer**| Logistics Coordinator | Inter-pump transfer execution | Stock Transfer Only |
| **Ordinary Staff** | Station Employee | Read-only or standard employee self-service | View Only |
| **Guest / Public** | Customers / General Public | Check points, view rewards catalog, view promotions | Public Portal Only |

---

## 2. Comprehensive Role Test Matrix

### Role 1: System Manager
- **Login:** Authenticates with full administrator credentials.
- **Dashboard:** Full Desk access with developer tools, bench settings, and CLP modules.
- **Navigation:** All standard and custom modules visible in sidebar.
- **View:** Unrestricted view across all DocTypes, audit logs, and settings.
- **Create:** Can create any document type in the system.
- **Update:** Can update any editable field.
- **Submit:** Can submit Fuel Purchase Entries, Gift Redemptions, Stock Entries, and Balance Adjustments.
- **Cancel:** Can cancel submitted documents with automatic ledger rollback.
- **Reports:** Unrestricted access to all 10 reports and database query reports.
- **Direct API:** Unrestricted execution of whitelisted APIs.
- **Logout:** Session cleared cleanly.
- **Verdict:** **PASS**

---

### Role 2: Pump Owner
- **Login:** Authenticates with Pump Owner credentials.
- **Dashboard:** CLP Workspace with executive metric cards, sales summaries, and stock levels.
- **Navigation:** Staff management, stock adjustments, customer lists, and all 10 reports.
- **View:** Can view customers, fuel purchases, stock ledgers, and staff accounts across owned pumps.
- **Create:** Can create staff accounts (`create_staff_account`), balance adjustments, and stock adjustments.
- **Update:** Can update customer records and pump settings.
- **Submit:** Can approve stock requests, submit balance adjustments, and approve redemptions.
- **Cancel:** Can cancel balance adjustments and redemptions (triggers automatic ledger rollback).
- **Reports:** Full access to all 10 custom reports with Excel/CSV export.
- **Direct API:** Authorized for `adjust_gift_stock`, `create_staff_account`, `deactivate_staff_account`, `get_staff_list`.
- **Restricted:** Cannot modify system DocTypes, install apps, or run bench commands.
- **Verdict:** **PASS**

---

### Role 3: Pump Manager
- **Login:** Authenticates with Station Manager credentials.
- **Dashboard:** Station-level CLP Workspace with daily sales and local gift stock metrics.
- **Navigation:** Customer management, fuel entry, gift redemption, gift stock requests, local sales reports.
- **View:** Scoped to station transactions and customer records.
- **Create:** Can register new customers, create fuel purchase entries, and request stock transfers.
- **Update:** Can edit unsubmitted transactions.
- **Submit:** Can submit fuel purchase entries and gift redemptions.
- **Cancel:** Cannot cancel submitted financial stock entries without owner approval.
- **Reports:** Authorized for daily sales, customer summary, and local stock reports.
- **Direct API:** Blocked from `create_staff_account`, `deactivate_staff_account`, and `adjust_gift_stock` (`PermissionError`).
- **Verdict:** **PASS**

---

### Role 4: CLM Incharge (Pump Attendant)
- **Login:** Authenticates with attendant PIN/password.
- **Dashboard:** Simplified mobile/desktop frontline interface.
- **Navigation:** Fast access to `Fuel Purchase Entry`, `Loyalty Customer`, and `Gift Redemption`.
- **View:** Customer search and point balance cards.
- **Create:** Can register customers with mandatory pump and space-free vehicle number.
- **Update:** Can input refuel liters.
- **Submit:** Can submit fuel purchases via the prominent bottom Save & Submit button.
- **Cancel:** Cannot cancel submitted refuel transactions or gift redemptions.
- **Reports:** Blocked from executive reports and activity audit logs.
- **Direct API:** Access restricted to `scan_and_process_qr`, `search_customer_for_scanner`, `check_customer_exists`.
- **Verdict:** **PASS**

---

### Role 5, 6, 7: CLP Stock Add, CLP Stock Subtract, CLP Stock Transfer
- **CLP Stock Add:**
  - Can initiate stock additions.
  - Blocked from stock subtraction or staff management.
- **CLP Stock Subtract:**
  - Can initiate stock issues/subtractions.
  - Prevented from driving stock negative.
- **CLP Stock Transfer:**
  - Can submit approved `Gift Stock Request` transfers between pump warehouses.
  - Automatically verifies stock availability before moving items.
- **Verdict:** **PASS**

---

### Role 8: Guest / Public Portal (`/loyality/check`)
- **Login:** No login required.
- **Dashboard / Portal:** Responsive customer self-service page.
- **Navigation:** Check Points, View Rewards Catalog, Petrol Pump Stations, Contact Support.
- **View:**
  - Query with mobile number -> Phone number masked (`******3210`), name masked (`Ramesh S***`).
  - Query with valid token -> Unmasked personal profile, purchase history, and redemptions.
- **Create / Update / Submit / Cancel:** Strictly blocked (Read-only portal).
- **Direct API:** Cannot access internal RPCs; guest endpoints enforce rate-limiting and PII sanitization.
- **Verdict:** **PASS**

---

## 3. Security Boundary Verification Summary

| Security Boundary | Verification Method | Enforcement Level | Status |
| :--- | :--- | :--- | :---: |
| **Owner Staff Management** | `_require_owner_or_manager()` in `clp/api.py` | Backend RPC Exception | **ENFORCED** |
| **Owner Stock Adjustments** | Role check in `adjust_gift_stock()` | Backend RPC Exception | **ENFORCED** |
| **Attendant Field Hiding** | Form layout properties in `fuel_purchase_entry.js` | UI Level Filter | **ENFORCED** |
| **Customer PII Masking** | Token vs Guest check in `check_loyalty_points()` | Backend Response Filter | **ENFORCED** |
| **Negative Inventory Guard** | Stock validation in `clp/api.py` & `gift_redemption.py` | Controller Validation | **ENFORCED** |
| **Unique Mobile Constraint** | Database unique check in `loyalty_customer.py` | ORM & DB Level | **ENFORCED** |
