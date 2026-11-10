# CLP Customer Loyalty Program – Full Application Test Report

**Target Domain:** `https://clp.hiideals.com`  
**Current Git Commit:** `f31e08c` | **Branch:** `main`  
**Base Commit:** `e5acab4`  
**Execution Environment:** Frappe v15 + MariaDB 10.6 + Redis  
**Audit Team:** Senior QA Automation & Acceptance Engineering Team  
**Date:** November 10, 2026  

---

## 1. Application Architecture & Inventory

The CLP system incorporates the following tested components:

### A. Core DocTypes
1. **`Loyalty Customer`:** Customer profiles, vehicle numbers, mobile numbers, cycle points, referral links, QR access tokens.
2. **`Fuel Purchase Entry`:** Submittable fuel transactions, liters, loyalty accruals, quick refuel action buttons.
3. **`Gift Redemption`:** Reward vouchers, multi-item rewards, points consumption, customer snapshot fields, stock issues.
4. **`Gift Redemption Item`:** Child table for individual gifts redeemed in a single redemption voucher.
5. **`Gift Stock Request`:** Inter-pump stock transfers, approval lifecycles, and ERPNext stock entry links.
6. **`Petrol Pump Location`:** Pump stations, warehouse mappings, active gift item associations, and contact details.
7. **`Pump Gift Item`:** Child table specifying required loyalty points per gift item at specific pumps.
8. **`CLP Customer Balance Adjustment`:** Owner point adjustments (Add, Subtract, Note Only) with reason and history tracking.
9. **`CLP Gift Stock Ledger`:** Immutable ledger of all gift item additions, deductions, and transfers.
10. **`CLP Activity Log`:** Security and operational audit log capturing user actions, timestamps, and before/after values.
11. **`User Pump Settings`:** User default pump and warehouse assignments.
12. **`CLP Referral Settings`:** Configurable referral reward points and thresholds.
13. **`Referral Reward Entry`:** Ledger tracking referral points earned and credited.

### B. Custom Reports
1. `Customer Loyalty Summary`
2. `Customer Registration Time Analysis`
3. `Daily Pump Sales Summary`
4. `Gift Item Stock Ledger Report`
5. `Gift Redemption Summary`
6. `Inactive Customers Report`
7. `Pump Wise Gift Stock`
8. `Referral Rewards Report`
9. `Registration Time Report`
10. `CLP Activity Audit Report`

### C. Portal & Desk Pages
1. `/loyality/check`: Public/customer self-service portal, point balance lookup, transaction history, and gift scheme info.
2. `/loyalty/check`: Backward-compatible redirect route pointing directly to `/loyality/check`.
3. `/app/clp`: Primary desk workspace with role-based metric cards, shortcuts, and quick links.
4. `/app/user-profile` & `/app/user/Administrator`: Profile management with direct photo upload.

---

## 2. End-to-End Workflow Verification

### Workflow 1: Attendant Refuel Operation
1. Attendant logs into `https://clp.hiideals.com`.
2. Default pump is automatically populated from `User Pump Settings`.
3. Attendant taps `📷 Scan QR` or types continuous vehicle number (`MH04GF6292`).
4. Customer info card renders with current points balance and registration pump.
5. Attendant enters liters (e.g., `45.0`).
6. Attendant clicks `💾 Save & Submit Purchase` at the bottom of the form.
7. Anti-double-click guard engages: button displays `⏳ Saving & Submitting...` and disables immediate secondary taps.
8. Transaction submits: customer balance increments by `45.0` liters.
9. Attendant clicks `➕ Next Refuel` to immediately initiate a fresh transaction.
- **Verdict:** **PASSED**

---

### Workflow 2: Gift Redemption & Stock Deduction
1. Attendant or Manager navigates to `/app/gift-redemption/new`.
2. Selects customer and petrol pump location.
3. System verifies warehouse matches petrol pump location.
4. Attendant adds gift items (e.g. `GIFT-WATCH-01`).
5. Child table validates stock availability at warehouse and populates required points from pump configuration.
6. Attendant clicks `Save` / `Submit`.
7. Customer points balance deducted; customer mobile snapshot and vehicle number recorded.
8. ERPNext Stock Entry (`Material Issue`) created and submitted; `CLP Gift Stock Ledger` entry recorded.
- **Verdict:** **PASSED**

---

### Workflow 3: Owner Staff Management
1. Pump Owner logs in and navigates to Staff Management.
2. Clicks `Add Staff` and enters `email: staff.highway@hiideals.com`, `name: Ramesh`, `role: CLM Incharge`, `pump: Main Pump Station`.
3. Calls backend endpoint `clp.api.create_staff_account`.
4. Creates `User`, assigns role, configures `User Pump Settings`.
5. New attendant logs in and immediately inherits default pump and operational permissions.
6. Owner can deactivate staff at any time via `clp.api.deactivate_staff_account`, revoking login while preserving all historical sales records.
- **Verdict:** **PASSED**

---

### Workflow 4: Inter-Pump Stock Transfer
1. Staff at Pump B requests stock from Pump A via `Gift Stock Request`.
2. Validates that source warehouse has sufficient stock.
3. Pump Owner or Admin reviews and approves request.
4. System creates ERPNext `Material Transfer` Stock Entry and posts corresponding Transfer Out / Transfer In ledger entries in `CLP Gift Stock Ledger`.
5. If cancelled, bidirectional reversals execute cleanly without inventory corruption.
- **Verdict:** **PASSED**

---

## 3. Form Layout & UI Navigation Testing

| Form / Page | Navigation Path | Save Button Position | Scrolling | Responsiveness | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Fuel Purchase Entry** | `/app/fuel-purchase-entry` | Bottom Center & Sticky | Smooth | Mobile & Desktop | **PASS** |
| **Loyalty Customer** | `/app/loyalty-customer` | Bottom Center & Sticky | Smooth | Mobile & Desktop | **PASS** |
| **Gift Redemption** | `/app/gift-redemption` | Bottom Center & Sticky | Smooth | Mobile & Desktop | **PASS** |
| **Gift Stock Request** | `/app/gift-stock-request` | Bottom Center & Sticky | Smooth | Mobile & Desktop | **PASS** |
| **User Profile / Administrator** | `/app/user-profile` | Direct Upload Button | Smooth | Mobile & Desktop | **PASS** |
| **Customer Portal** | `/loyality/check` | Responsive Action Bar | Smooth | Mobile & Desktop | **PASS** |
