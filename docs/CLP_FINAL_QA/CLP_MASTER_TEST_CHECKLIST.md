# CLP Customer Loyalty Program – Master Test Checklist (Final QA & Acceptance)

**Project:** Customer Loyalty Program (CLP)  
**Target Domain:** `https://clp.hiideals.com`  
**Current Git Commit:** `f31e08c` | **Branch:** `main`  
**Base Commit:** `e5acab4`  
**Audit Date:** November 10, 2026  
**Auditing Team:** Senior QA Automation & Acceptance Engineering Team  

---

## 1. Customer Requirements Master Checklist (16 Requirements)

| ID | Requirement | Backend | Database | Web | Mobile | Permission | Test Evidence | Result |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **REQ-01** | Customer QR Transaction History | ☑ | ☑ | ☑ | ☑ | ☑ | Token lookup in `clp/api.py`, `/loyality/check`, `Loyalty Customer.qr_access_token` | **PASS** |
| **REQ-02** | Petrol Pump Selection During Registration | ☑ | ☑ | ☑ | ☑ | ☑ | Mandatory `registration_pump` in `loyalty_customer.py:validate()`, pump filtering | **PASS** |
| **REQ-03** | Owner-Only Stock Management | ☑ | ☑ | ☑ | ☑ | ☑ | `adjust_gift_stock` enforces System Manager/Pump Owner role in `clp/api.py` | **PASS** |
| **REQ-04** | User Point Adjustments and Notes | ☑ | ☑ | ☑ | ☑ | ☑ | `CLPCustomerBalanceAdjustment`: Add, Subtract, Note Only, balance audit trail | **PASS** |
| **REQ-05** | Staff Account Creation | ☑ | ☑ | ☑ | ☑ | ☑ | `create_staff_account` owner-only RPC, role assignment, `User Pump Settings` | **PASS** |
| **REQ-06** | Staff Account Deactivation | ☑ | ☑ | ☑ | ☑ | ☑ | `deactivate_staff_account` sets `enabled=0`, preserves historical activity | **PASS** |
| **REQ-07** | Vehicle Registration Validation | ☑ | ☑ | ☑ | ☑ | ☑ | Space rejection (`MH 04 GF 6292` -> Error), continuous format enforced | **PASS** |
| **REQ-08** | Vehicle Search Validation | ☑ | ☑ | ☑ | ☑ | ☑ | `check_loyalty_points` rejects space-containing vehicle searches with guidance | **PASS** |
| **REQ-09** | Unique Mobile & Duplicate Vehicle | ☑ | ☑ | ☑ | ☑ | ☑ | Unique phone validation (`tabLoyalty Customer`), duplicate vehicle allowed | **PASS** |
| **REQ-10** | Remove Fuel Type & Amount Fields | ☑ | ☑ | ☑ | ☑ | ☑ | `fuel_purchase_entry.js` hides `amount` & `fuel_type` for attendants, keeps DB intact | **PASS** |
| **REQ-11** | Fuel Entry Attendant Workflow | ☑ | ☑ | ☑ | ☑ | ☑ | Sticky bottom Save button, anti-double-click guard, submit spinner, 1 refuel = 1 txn | **PASS** |
| **REQ-12** | Registration Date Analytics | ☑ | ☑ | ☑ | ☑ | ☑ | `customer_registration_time_analysis` report with daily/monthly date filters | **PASS** |
| **REQ-13** | Detailed Reporting Suite (10 Reports) | ☑ | ☑ | ☑ | ☑ | ☑ | 10 custom reports verified with SQL aggregation, filters, and CSV/Excel export | **PASS** |
| **REQ-14** | Public QR Information Page | ☑ | ☑ | ☑ | ☑ | ☑ | Public portal hides PII (masked mobile `******3210`), shows catalogue & schemes | **PASS** |
| **REQ-15** | Activity Audit Logs | ☑ | ☑ | ☑ | ☑ | ☑ | Immutable `CLP Activity Log` records all customer, stock, staff, and balance events | **PASS** |
| **REQ-16** | Gift Stock and Issuance History | ☑ | ☑ | ☑ | ☑ | ☑ | `gift_item_stock_ledger_report.py` displays recipient, vehicle, mobile, in/out balances | **PASS** |

---

## 2. Verification Legend

- **PASS:** Fully implemented, verified via automated test suites and codebase inspection, conforming to business acceptance criteria.
- **FAIL:** Requirement broken or not conforming to specification.
- **PARTIAL:** Feature partially working with minor cosmetic or non-blocking issues.
- **BLOCKED:** Test could not be executed due to external environment or hardware dependency.
- **NOT IMPLEMENTED:** Capability absent from application.
- **NOT VERIFIED:** Item awaiting manual execution.
