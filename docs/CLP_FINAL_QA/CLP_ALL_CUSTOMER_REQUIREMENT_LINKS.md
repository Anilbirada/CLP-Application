# CLP Customer Loyalty Program – All Customer Requirement Links Directory

**Target Production Domain:** `https://clp.hiideals.com`  
**Current Git Commit:** `f31e08c` | **Branch:** `main`  
**Base Commit:** `e5acab4`  
**Audit Team:** Senior QA Automation & Acceptance Engineering Team  
**Date:** November 10, 2026  

---

## 1. Customer Requirements Link Matrix (All 16 Requirements)

| Req ID | Feature | Direct Web URL | API Endpoint | Required Role | Mobile Screen | Link Status |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **REQ-01** | Customer QR Transaction History | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.check_loyalty_points` | Guest / Token | History Screen | **WORKING** |
| **REQ-02** | Petrol Pump Selection Registration | `https://clp.hiideals.com/app/loyalty-customer/new` | `/api/method/frappe.client.insert` | CLM Incharge | New Customer Screen | **LOGIN REQUIRED** |
| **REQ-03** | Owner-Only Stock Management | `https://clp.hiideals.com/app/clp` | `/api/method/clp.api.adjust_gift_stock` | Pump Owner | N/A (Desk Only) | **ROLE ACCESS REQUIRED** |
| **REQ-04** | User Point Adjustments & Notes | `https://clp.hiideals.com/app/clp-customer-balance-adjustment` | `/api/method/frappe.client.insert` | Pump Owner | Adjust Balance Screen | **ROLE ACCESS REQUIRED** |
| **REQ-05** | Staff Account Creation | `https://clp.hiideals.com/app/user/new` | `/api/method/clp.api.create_staff_account` | Pump Owner | N/A (Desk Only) | **ROLE ACCESS REQUIRED** |
| **REQ-06** | Staff Account Deactivation | `https://clp.hiideals.com/app/user` | `/api/method/clp.api.deactivate_staff_account` | Pump Owner | N/A (Desk Only) | **ROLE ACCESS REQUIRED** |
| **REQ-07** | Vehicle Registration Validation | `https://clp.hiideals.com/app/loyalty-customer/new` | `/api/method/frappe.client.insert` | CLM Incharge | New Customer Screen | **LOGIN REQUIRED** |
| **REQ-08** | Vehicle Search Validation | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.check_loyalty_points` | Guest / Staff | Customer Search Screen | **WORKING** |
| **REQ-09** | Unique Mobile & Duplicate Vehicle | `https://clp.hiideals.com/app/loyalty-customer/new` | `/api/method/frappe.client.insert` | CLM Incharge | New Customer Screen | **LOGIN REQUIRED** |
| **REQ-10** | Remove Fuel Type & Amount Fields | `https://clp.hiideals.com/app/fuel-purchase-entry/new` | `/api/method/frappe.client.insert` | CLM Incharge | Fuel Entry Screen | **LOGIN REQUIRED** |
| **REQ-11** | Fuel Entry Attendant Workflow | `https://clp.hiideals.com/app/fuel-purchase-entry/new` | `/api/method/frappe.client.insert` | CLM Incharge | Fuel Entry Screen | **LOGIN REQUIRED** |
| **REQ-12** | Registration Date Analytics | `https://clp.hiideals.com/app/query-report/Customer%20Registration%20Time%20Analysis` | `/api/method/frappe.desk.query_report.run` | Pump Owner | Reports Dashboard | **ROLE ACCESS REQUIRED** |
| **REQ-13** | Detailed Reporting Suite | `https://clp.hiideals.com/app/query-report/Gift%20Item%20Stock%20Ledger%20Report` | `/api/method/frappe.desk.query_report.run` | Pump Owner | Reports Dashboard | **ROLE ACCESS REQUIRED** |
| **REQ-14** | Public QR Information Page | `https://clp.hiideals.com/loyality/check` | `/api/method/clp.api.get_customer_rewards_catalog` | Guest (Public) | Public Portal View | **WORKING** |
| **REQ-15** | Activity Audit Logs | `https://clp.hiideals.com/app/clp-activity-log` | `/api/method/frappe.client.get_list` | Pump Owner | N/A (Desk Only) | **ROLE ACCESS REQUIRED** |
| **REQ-16** | Gift Stock and Issuance History | `https://clp.hiideals.com/app/query-report/Gift%20Item%20Stock%20Ledger%20Report` | `/api/method/frappe.desk.query_report.run` | Pump Owner | Reports Dashboard | **ROLE ACCESS REQUIRED** |

---

## 2. Complete Application Feature & Page Directory

### Core Application Pages
1. **Login Page:** `https://clp.hiideals.com/login` | Status: **WORKING**
2. **Owner / Staff CLP Workspace:** `https://clp.hiideals.com/app/clp` | Status: **LOGIN REQUIRED**
3. **Customer Registration Form:** `https://clp.hiideals.com/app/loyalty-customer/new` | Status: **LOGIN REQUIRED**
4. **Customer List View:** `https://clp.hiideals.com/app/loyalty-customer` | Status: **LOGIN REQUIRED**
5. **Fuel Purchase Entry Form:** `https://clp.hiideals.com/app/fuel-purchase-entry/new` | Status: **LOGIN REQUIRED**
6. **Fuel Purchase List View:** `https://clp.hiideals.com/app/fuel-purchase-entry` | Status: **LOGIN REQUIRED**
7. **Gift Redemption Form:** `https://clp.hiideals.com/app/gift-redemption/new` | Status: **LOGIN REQUIRED**
8. **Gift Redemption List View:** `https://clp.hiideals.com/app/gift-redemption` | Status: **LOGIN REQUIRED**
9. **Gift Stock Request (Transfer) Form:** `https://clp.hiideals.com/app/gift-stock-request/new` | Status: **LOGIN REQUIRED**
10. **Gift Stock Request List View:** `https://clp.hiideals.com/app/gift-stock-request` | Status: **LOGIN REQUIRED**
11. **Balance Adjustment Form:** `https://clp.hiideals.com/app/clp-customer-balance-adjustment/new` | Status: **ROLE ACCESS REQUIRED**
12. **Petrol Pump Location List:** `https://clp.hiideals.com/app/petrol-pump-location` | Status: **LOGIN REQUIRED**
13. **Staff Management View:** `https://clp.hiideals.com/app/user` | Status: **ROLE ACCESS REQUIRED**
14. **Activity Audit Log:** `https://clp.hiideals.com/app/clp-activity-log` | Status: **ROLE ACCESS REQUIRED**
15. **User Profile View:** `https://clp.hiideals.com/app/user-profile` | Status: **LOGIN REQUIRED**
16. **Administrator Profile:** `https://clp.hiideals.com/app/user/Administrator` | Status: **ROLE ACCESS REQUIRED**

### Custom Reports Directory
1. **Customer Loyalty Summary:** `https://clp.hiideals.com/app/query-report/Customer%20Loyalty%20Summary` | Status: **ROLE ACCESS REQUIRED**
2. **Customer Registration Time Analysis:** `https://clp.hiideals.com/app/query-report/Customer%20Registration%20Time%20Analysis` | Status: **ROLE ACCESS REQUIRED**
3. **Daily Pump Sales Summary:** `https://clp.hiideals.com/app/query-report/Daily%20Pump%20Sales%20Summary` | Status: **ROLE ACCESS REQUIRED**
4. **Gift Item Stock Ledger Report:** `https://clp.hiideals.com/app/query-report/Gift%20Item%20Stock%20Ledger%20Report` | Status: **ROLE ACCESS REQUIRED**
5. **Gift Redemption Summary:** `https://clp.hiideals.com/app/query-report/Gift%20Redemption%20Summary` | Status: **ROLE ACCESS REQUIRED**
6. **Inactive Customers Report:** `https://clp.hiideals.com/app/query-report/Inactive%20Customers%20Report` | Status: **ROLE ACCESS REQUIRED**
7. **Pump Wise Gift Stock:** `https://clp.hiideals.com/app/query-report/Pump%20Wise%20Gift%20Stock` | Status: **ROLE ACCESS REQUIRED**
8. **Referral Rewards Report:** `https://clp.hiideals.com/app/query-report/Referral%20Rewards%20Report` | Status: **ROLE ACCESS REQUIRED**
9. **Registration Time Report:** `https://clp.hiideals.com/app/query-report/Registration%20Time%20Report` | Status: **ROLE ACCESS REQUIRED**
10. **CLP Activity Audit Report:** `https://clp.hiideals.com/app/query-report/CLP%20Activity%20Audit%20Report` | Status: **ROLE ACCESS REQUIRED**

### Public & Customer Portal Routes
1. **Customer Portal (Active Route):** `https://clp.hiideals.com/loyality/check` | Status: **WORKING**
2. **Customer Portal (Legacy Redirect):** `https://clp.hiideals.com/loyalty/check` | Status: **WORKING**
