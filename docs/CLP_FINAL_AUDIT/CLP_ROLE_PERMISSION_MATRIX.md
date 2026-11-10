# CLP Customer Loyalty Program – Role Permission Matrix

**Target Production Domain:** `https://clp.hiideals.com`  
**Base Commit:** `0f66021` | **Audit Branch:** `feat/final-audit-verification`  
**Date:** November 10, 2026  

---

## 1. DocType Permission Matrix

| DocType | System Manager | Pump Owner | Pump Manager | CLM Incharge | Frontline Staff | Guest / Public |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Loyalty Customer`** | Create, Read, Write, Delete, Export | Create, Read, Write, Export | Create, Read, Write | Create, Read, Write | Read | None (Portal via Token/Search only) |
| **`Fuel Purchase Entry`** | Full (Submit, Cancel, Amend) | Full (Submit, Cancel, Amend) | Create, Read, Write, Submit | Create, Read, Write, Submit | Read | None |
| **`Gift Redemption`** | Full (Submit, Cancel, Amend) | Full (Submit, Cancel, Amend) | Create, Read, Write, Submit | Create, Read, Write, Submit | Read | None |
| **`Gift Stock Request`** | Full (Approve, Submit, Cancel) | Full (Approve, Submit, Cancel) | Create, Read (Request Only) | Read Only | None | None |
| **`Petrol Pump Location`** | Create, Read, Write, Delete | Create, Read, Write | Read Only | Read Only | Read Only | Public Info on Portal |
| **`CLP Customer Balance Adjustment`** | Full (Submit, Cancel, Amend) | Full (Submit, Cancel, Amend) | Read Only | Read Only | None | None |
| **`CLP Gift Stock Ledger`** | Read, Report, Export | Read, Report, Export | Read, Report | Read Only | None | None |
| **`CLP Activity Log`** | Read, Report, Export | Read, Report, Export | Read Only | Read Only | None | None |
| **`User Pump Settings`** | Full Access | Full Access | Read Only | Read (Own Only) | None | None |
| **`User` (Staff Accounts)** | Full Access | Create/Deactivate via RPC | None | None | None | None |

---

## 2. API Method Authorization Matrix

| API Method | Allowed Roles | Guest Allowed? | Enforcement Mechanism |
| :--- | :--- | :---: | :--- |
| **`clp.api.check_loyalty_points`** | Public, All Roles | **YES** | Field-level masking for guests; unmasked for staff or valid token holders. Rate limited (30/min). |
| **`clp.api.scan_and_process_qr`** | System Manager, Pump Owner, Pump Manager, CLM Incharge | **NO** | `_require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})` |
| **`clp.api.search_customer_for_scanner`** | System Manager, Pump Owner, Pump Manager, CLM Incharge | **NO** | `_require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})` |
| **`clp.api.get_whatsapp_link`** | System Manager, Pump Owner, Pump Manager, CLM Incharge | **NO** | `_require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})` |
| **`clp.api.generate_qr_image`** | System Manager, Pump Owner, Pump Manager, CLM Incharge | **NO** | `_require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})` |
| **`clp.api.adjust_gift_stock`** | System Manager, Pump Owner | **NO** | `if not (_has_role("System Manager") or _has_role("Pump Owner")): frappe.throw(PermissionError)` |
| **`clp.api.create_staff_account`** | System Manager, Pump Owner | **NO** | `_require_owner_or_manager()` |
| **`clp.api.deactivate_staff_account`** | System Manager, Pump Owner | **NO** | `_require_owner_or_manager()` |
| **`clp.api.get_staff_list`** | System Manager, Pump Owner | **NO** | `_require_owner_or_manager()` |
| **`clp.api.get_user_default_pump`** | Authenticated CLP Users | **NO** | `frappe.session.user` query on `User Pump Settings` |
| **`clp.api.update_customer_profile`** | Token Holder / Customer | **YES** | Validates 32-character `qr_access_token` existence |

---

## 3. Reporting Role Permissions

| Report | Viewer Roles |
| :--- | :--- |
| **Customer Loyalty Summary** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Customer Registration Time Analysis** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Daily Pump Sales Summary** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Gift Item Stock Ledger Report** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Gift Redemption Summary** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Inactive Customers Report** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Pump Wise Gift Stock** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **Referral Rewards Report** | `System Manager`, `Pump Owner`, `CLP Referral Manager` |
| **Registration Time Report** | `System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`, `CLP Reports Viewer` |
| **CLP Activity Audit Report** | `System Manager`, `Pump Owner` |
