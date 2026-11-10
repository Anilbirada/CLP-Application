# CLP Customer Loyalty Program – Database Schema & Stock Architecture Audit

**Target Production Domain:** `https://clp.hiideals.com`  
**Database Engine:** MariaDB 10.6+ / InnoDB  
**Base Commit:** `0f66021` | **Audit Branch:** `feat/final-audit-verification`  
**Date:** November 10, 2026  

---

## 1. Single Source of Truth Stock Architecture

The CLP stock subsystem coordinates between Frappe/ERPNext core inventory and the customer loyalty rewards program:

```
[ERPNext Stock Entry] (Material Receipt / Issue / Transfer)
         │
         ▼
[tabStock Ledger Entry] (Authoritative ERPNext inventory transaction history)
         │
         ▼
     [tabBin] (Physical actual_qty in warehouse)
         │
         ▼
[tabCLP Gift Stock Ledger] (Immutable CLP business history with skip_bin_sync=True)
```

### Key Principles Verified:
1. **No Duplicate Bin Updates:**
   - In [`clp/stock.py`](file:///E:/clp%20updated%20code/clp-code-reviewed-fixed-1/clp-develop/clp/stock.py), direct SQL updates to `tabBin` are strictly guarded behind `if not is_erpnext_installed and not skip_bin_sync:`.
   - When ERPNext is installed, submitting an ERPNext `Stock Entry` automatically handles `tabBin.actual_qty` via ERPNext's native stock ledger pipeline.
2. **Transaction Atomicity:**
   - Manual `frappe.db.commit()` calls were eliminated across `stock.py`. Transactions commit or rollback atomically with document lifecycle events.
3. **Cancellation & Reversals:**
   - When a `Gift Redemption` is cancelled, `gift_redemption.py:on_cancel` cancels the linked `Stock Entry` directly (`se.cancel()`), and records the reversal in `tabCLP Gift Stock Ledger` with `skip_bin_sync=has_se_cancelled`. This guarantees zero double-restorations.
   - When a `Gift Stock Request` is cancelled, `gift_stock_request.py:on_cancel` cancels the linked `Stock Entry` and reverses source and target pump movements with `skip_bin_sync=has_se_cancelled`.

---

## 2. Stock Lifecycles Detailed Analysis

### A. Stock Addition (Receipt)
1. Owner calls `clp.api.adjust_gift_stock(item_code, warehouse, qty, action="add", reason=...)`.
2. Validates caller has `Pump Owner` or `System Manager` role.
3. Creates and submits ERPNext `Stock Entry` (type: `Material Receipt`).
4. ERPNext creates `Stock Ledger Entry` rows and increments `tabBin.actual_qty` for that warehouse by `+qty`.
5. Records CLP movement in `tabCLP Gift Stock Ledger` (`voucher_type: "Stock Addition"`, `qty_change: +qty`, `skip_bin_sync=True`).
6. Stock balance reflects exact addition.

### B. Stock Subtraction (Issue / Manual Adjustment)
1. Owner calls `clp.api.adjust_gift_stock(..., action="remove")`.
2. Verifies current available stock in `tabBin` $\ge$ requested quantity. Throws validation error if insufficient.
3. Creates and submits ERPNext `Stock Entry` (type: `Material Issue`).
4. ERPNext decrements `tabBin.actual_qty` by `-qty`.
5. Records CLP movement in `tabCLP Gift Stock Ledger` (`voucher_type: "Stock Subtraction"`, `qty_change: -qty`, `skip_bin_sync=True`).

### C. Stock Transfer (Inter-Pump)
1. Manager submits `Gift Stock Request` specifying source pump/warehouse and target pump/warehouse.
2. Validates source and target warehouses are different and belong to respective pumps.
3. Owner approves request.
4. On approval, `gift_stock_request.py` creates and submits ERPNext `Stock Entry` (type: `Material Transfer`).
5. ERPNext moves inventory from source warehouse to target warehouse in `tabBin`.
6. Records two entries in `tabCLP Gift Stock Ledger`:
   - Outgoing from source pump (`qty_change: -qty`, `skip_bin_sync=True`).
   - Incoming to target pump (`qty_change: +qty`, `skip_bin_sync=True`).

### D. Gift Redemption
1. Attendant submits `Gift Redemption`.
2. System authoritative check: validates gift item points from `tabPump Gift Item` (client-submitted points are ignored).
3. Verifies customer has sufficient cycle points or `allow_negative_balance` is enabled.
4. Verifies warehouse stock in `tabBin` $\ge$ redeemed gift quantity.
5. Deducts points from customer's `current_cycle_liters`.
6. Creates ERPNext `Stock Entry` (type: `Material Issue`).
7. Decrements `tabBin.actual_qty` exactly once.
8. Records CLP movement in `tabCLP Gift Stock Ledger` (`voucher_type: "Gift Redemption"`, `qty_change: -1`, `skip_bin_sync=True`).

---

## 3. Database Schema & Tables

### Primary CLP Tables
1. **`tabLoyalty Customer`:**
   - `name`: Primary key (`MANUAL-####` or `QR-####`).
   - `customer_name`: Full customer name.
   - `mobile_number`: Unique mobile number (indexed, unique constraint).
   - `vehicle_number`: Uppercase, space-free vehicle registration number (indexed, multi-vehicle allowed).
   - `registration_pump`: Link to `tabPetrol Pump Location` (mandatory for new docs).
   - `current_cycle_liters`: Active loyalty points available for redemption.
   - `total_liters_purchased`: Cumulative fuel purchased across all cycles.
   - `total_gifts_received`: Total count of redeemed gifts.
   - `qr_access_token`: Unique 32-character high-entropy token for customer portal authorization.
   - `status`: Select (`Active`, `Inactive`).

2. **`tabFuel Purchase Entry`:**
   - `name`: Primary key (`FPE-#####`).
   - `petrol_pump`: Link to `tabPetrol Pump Location`.
   - `customer`: Link to `tabLoyalty Customer`.
   - `liters`: Purchased fuel volume.
   - `amount`: Transaction amount (hidden from attendant interface).
   - `fuel_type`: Fuel grade (hidden from attendant interface).
   - `purchase_date`: Timestamp of purchase.
   - `docstatus`: Document status (`0` = Draft, `1` = Submitted, `2` = Cancelled).

3. **`tabGift Redemption`:**
   - `name`: Primary key (`GIFT-#####`).
   - `customer`: Link to `tabLoyalty Customer`.
   - `customer_mobile`: Snapshot of customer mobile at redemption time.
   - `vehicle_number`: Snapshot of vehicle number at redemption time.
   - `petrol_pump`: Link to `tabPetrol Pump Location`.
   - `warehouse`: Link to `tabWarehouse`.
   - `stock_entry`: Link to ERPNext `tabStock Entry`.
   - `total_points`: Total loyalty points deducted.

4. **`tabCLP Gift Stock Ledger`:**
   - `name`: Unique hash.
   - `posting_datetime`: Exact posting timestamp.
   - `petrol_pump`: Link to `tabPetrol Pump Location`.
   - `gift_item`: Link to `tabItem`.
   - `voucher_type`: Transaction type (`Stock Addition`, `Stock Subtraction`, `Stock Transfer In`, `Stock Transfer Out`, `Gift Redemption`).
   - `voucher_no`: Linked document name.
   - `qty_change`: Signed quantity change.
   - `balance_qty`: Running balance at that pump.
   - `user`: Link to `tabUser`.

5. **`tabCLP Activity Log`:**
   - `name`: Unique hash.
   - `event_datetime`: Timestamp.
   - `actor`: User who initiated action.
   - `action`: Document event (`after_insert`, `on_submit`, `on_cancel`, `update`).
   - `reference_doctype`: Target DocType.
   - `reference_name`: Target document ID.
   - `details`: JSON payload containing context, point adjustments, and reason.

---

## 4. Discrepancy Reconciliation Guidelines

If historical discrepancies exist between `tabBin.actual_qty` and `tabCLP Gift Stock Ledger` prior to this fix:
1. Generate the reconciliation discrepancy report using ERPNext `Stock Balance` vs `Gift Item Stock Ledger Report`.
2. Do **NOT** execute automated bulk updates without pump owner review.
3. Post approved adjustments using standard `Stock Reconciliation` in ERPNext, which automatically records audited correction entries.
