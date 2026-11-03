# CLP Mobile Application – Architecture & API Integration Specification
## Phase 1: Existing Backend Audit, API Inventory & Mobile Feature Mapping

**Project:** Customer Loyalty Program (CLP)  
**Organization:** RSR Technology  
**Client:** Hiideals  
**Existing Production Web Application:** `https://clp.hiideals.com`  
**Backend Framework:** Frappe Framework v15 / ERPNext (Python, MariaDB, Redis)  
**Mobile Framework:** Expo + React Native + TypeScript  

---

## 1. Executive Summary & Critical Architectural Invariants

The Customer Loyalty Program (CLP) mobile application is engineered as a first-class native client (Android & iOS) designed to operate synchronously alongside the existing Frappe web application and Desk portals.

### Single Source of Truth
* **Zero Backend Duplication:** No secondary backend, microservice, or proxy database is introduced. The Frappe v15 MariaDB instance remains the sole authoritative source of truth.
* **Unified Loyalty Engine:** All point calculations, liters balances (`current_cycle_liters`), lifetime totals (`total_liters_purchased`), gift redemptions (`total_gifts_received`), stock deductions, and referral rewards are strictly evaluated, verified, and executed by the Frappe backend.
* **Zero Client Calculation:** The mobile application is purely a presentation, telemetry, and request orchestration layer; it never calculates or mutates point balances locally.
* **Web App Continuity:** The existing web application (`https://clp.hiideals.com`), Desk views, QR redirects, and public portals continue functioning without regression or schema conflicts.

```
                           +---------------------------------------+
                           |         CLOUDFLARE EDGE CDN           |
                           |       https://clp.hiideals.com        |
                           +-------------------+-------------------+
                                               |
                     +-------------------------+-------------------------+
                     |                                                   |
                     v                                                   v
       +----------------------------+                     +----------------------------+
       |   EXISTING WEB APP / DESK  |                     |  NEW EXPO REACT NATIVE APP |
       |     (Frappe Web & Desk)    |                     |      (Android & iOS)       |
       +--------------+-------------+                     +--------------+-------------+
                      |                                                  |
                      |           HTTPS REST APIs / Whitelisted          |
                      +------------------------+-------------------------+
                                               |
                                               v
                           +---------------------------------------+
                           |       FRAPPE v15 PYTHON BACKEND       |
                           |   (clp.api, Controllers, DocTypes)   |
                           +-------------------+-------------------+
                                               |
                     +-------------------------+-------------------------+
                     |                         |                         |
                     v                         v                         v
           +-------------------+     +-------------------+     +-------------------+
           | MariaDB Database  |     |   Redis Queues    |     | Gift Stock Ledger |
           | (Single Source)   |     | (Cache & Workers) |     |  & Warehouse Bin  |
           +-------------------+     +-------------------+     +-------------------+
```

---

## 2. Existing CLP Backend Audit & System Inspection

### 2.1 Core DocTypes & Relational Schema

| DocType | Role / Purpose | Key Fields | Authoritative Business Rules |
| :--- | :--- | :--- | :--- |
| **`Loyalty Customer`** | Core customer identity & loyalty ledger account | `name` (ID / Naming Series / Pre-printed QR), `customer_name`, `mobile_number` (Unique, 10-digit), `vehicle_number` (Normalized uppercase), `status` (Active/Inactive), `registration_date`, `registration_pump`, `current_cycle_liters` (Active Points), `total_liters_purchased`, `total_gifts_received`, `last_gift_date`, `referred_by_customer`, `referral_points_balance`, `qr_access_token` (32-byte secure token) | Unique mobile number enforced. Vehicle number normalized without whitespace. Single source of active points balance. |
| **`Fuel Purchase Entry`** | Transaction record of fuel sales | `name`, `customer`, `customer_name`, `vehicle_number`, `petrol_pump`, `pump_name`, `purchase_date`, `fuel_type` (Petrol, Diesel, CNG, etc.), `liters`, `amount`, `slip_no` | On submit (`docstatus=1`), increments `customer.current_cycle_liters` and `customer.total_liters_purchased`. Evaluates referral bonus if `CLP Referral Settings` enabled. Reverses balances on cancel (`docstatus=2`). |
| **`Gift Redemption`** | Claim & disbursement of loyalty rewards | `name`, `customer`, `customer_name`, `petrol_pump`, `warehouse`, `redemption_date`, `liters_accumulated`, `total_points`, `items` (child table), `gift_given_by`, `stock_entry` | Validates customer balance, warehouse stock in `Bin` or `CLP Gift Stock Ledger`. Deducts `total_points` from `current_cycle_liters`, increments `total_gifts_received`, records stock reduction. Supports reversible cancellation. |
| **`Gift Redemption Item`** | Child table for multiple gift items per redemption | `parent`, `gift_item` (Item code), `item_name`, `points_required` | Inherits authoritative points required from `Petrol Pump Location`. Rejects client-tampered point values. |
| **`Petrol Pump Location`** | Station location & inventory warehouse mapping | `name`, `pump_name`, `pump_code`, `address`, `warehouse`, `is_active`, `gift_items` (child table) | Defines local reward catalog and warehouse for stock deductions. |
| **`Pump Gift Item`** | Child table of gifts configured for a station | `gift_item`, `item_name`, `points_required`, `available_stock`, `description` | Defines points threshold per reward at each pump location. |
| **`CLP Gift Stock Ledger`** | Immutable stock movement ledger | `petrol_pump`, `gift_item`, `posting_datetime`, `voucher_type`, `qty_change`, `balance_qty`, `user` | Audit log of all stock increases, adjustments, and redemptions. Synchronizes `tabBin.actual_qty`. |
| **`CLP Referral Settings`** | Global referral program parameters | `enabled`, `points_per_eligible_purchase`, `minimum_purchase_amount` | Single DocType governing referral reward rules. |
| **`Referral Reward Entry`** | Ledger of referral bonuses | `referrer`, `referred_customer`, `fuel_purchase_entry`, `points_awarded`, `status` | Linked idempotently to `Fuel Purchase Entry`. |

---

## 3. Existing API Inventory & Audit

### 3.1 Public / Guest-Accessible APIs

| API Endpoint | HTTP Method | Rate Limit | Purpose & Payload | Reusability in Mobile App |
| :--- | :--- | :--- | :--- | :--- |
| `clp.api.check_loyalty_points` | `GET` / `POST` | 30 req / 60s per IP | Accepts `vehicle` or `mobile`. Returns customer profile, points balance, last 15 purchases, last 10 redemptions. | **Directly Reusable**: Ideal for quick status check, login validation, and guest lookup. |
| `clp.api.get_customer_portal_by_token` | `GET` | Standard | Accepts `token` (32-byte QR token). Returns customer profile (masked mobile), purchase history, and redemptions. | **Directly Reusable**: Ideal for QR code scan deep-linking and authenticated token session validation. |

### 3.2 Staff / Incharge-Restricted APIs (Requires Frappe Role)

| API Endpoint | HTTP Method | Permitted Roles | Purpose & Reusability |
| :--- | :--- | :--- | :--- |
| `clp.api.scan_and_process_qr` | `POST` | `CLP_STAFF_ROLES` | Scans customer QR string, validates customer exists, returns details. Reusable in Staff Mode. |
| `clp.api.search_customer_for_scanner` | `GET` | `CLP_STAFF_ROLES` | Autocomplete search by mobile, vehicle, or ID. Reusable in Staff Mode. |
| `clp.api.create_quick_sale` | `POST` | `CLP_STAFF_ROLES` | Dispenser/Cashier creates new fuel sale directly. Reusable in Staff Mode. |
| `clp.api.get_available_gifts` | `GET` | `CLP_STAFF_ROLES` | Returns gifts configured for a pump with live stock. Reusable in Staff Mode. |
| `clp.api.get_gift_item_details` | `GET` | `CLP_STAFF_ROLES` | Returns details for a single gift item. Reusable in Staff Mode. |
| `clp.api.adjust_gift_stock` | `POST` | `CLP_STAFF_ROLES` | Adds/subtracts warehouse stock with ledger logging. Reusable in Staff Mode. |
| `clp.api.get_user_default_pump` | `GET` | `CLP_STAFF_ROLES` | Retrieves the station assigned to the logged-in staff member. Reusable in Staff Mode. |

---

## 4. Gap Analysis & Proposed Backend Additions

To deliver the customer-facing mobile application features without compromising security or breaking web views, the following lightweight, additive API methods are identified for the Frappe backend:

| Gap Area | Missing Capability in Current Backend | Solution / Proposed Additive API | Implementation Strategy |
| :--- | :--- | :--- | :--- |
| **Customer Auth & Session** | Mobile customer requires persistent token-based session without sharing full ERPNext password. | `clp.api.customer_mobile_login` | Authenticates customer by registered mobile number (or vehicle + mobile), verifies status, generates/returns session token and profile for `SecureStore`. |
| **Public Rewards Catalog** | `get_available_gifts` requires staff role; customers cannot browse rewards catalogue. | `clp.api.get_customer_rewards_catalog` | Whitelisted public/customer method. Queries active pump gift items with points required and stock status. |
| **Customer Redemption Request** | Customers cannot create `Gift Redemption` DocType directly due to Frappe role permissions. | `clp.api.request_customer_redemption` | Validates customer token, checks point balance, verifies stock, issues a redemption claim / voucher with an idempotency key to prevent double deduction. |
| **Customer Profile Updates** | Customers cannot update vehicle/contact info through standard desk APIs. | `clp.api.update_customer_profile` | Validates customer token, sanitizes input, updates permitted customer fields safely. |
| **Customer Notifications** | No unified notification feed for customer activity. | `clp.api.get_customer_notifications` | Aggregates recent fuel purchases, points additions, redemptions, and referral bonuses into a chronological activity feed. |

---

## 5. Mobile Feature Mapping (12 Modules)

| # | Mobile Module | Target Screen | Backend Integration | Data Source / APIs |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Splash Screen** | `app/index.tsx` | App startup, token check in `SecureStore`, theme initialization | Local cache + `clp.api.get_customer_portal_by_token` |
| 2 | **Authentication** | `app/(auth)/login.tsx` | Mobile number verification, staff credentials login, session persistence | `clp.api.customer_mobile_login` & `/api/method/login` |
| 3 | **Customer Dashboard** | `app/(customer)/dashboard.tsx` | Active points (`current_cycle_liters`), lifetime liters, recent fuel purchases, quick actions, promo banners | `clp.api.check_loyalty_points` or `clp.api.get_customer_portal_by_token` |
| 4 | **Customer Profile** | `app/(customer)/profile.tsx` | Customer name, mobile number, vehicle number, registration date, pump info | `tabLoyalty Customer` via customer session |
| 5 | **Loyalty Points** | `app/(customer)/loyalty-points.tsx` | Balance card, points milestone progress bar, referral points, points history | `tabLoyalty Customer`, `Fuel Purchase Entry`, `Gift Redemption` |
| 6 | **Fuel Transactions** | `app/(customer)/transactions.tsx` | Chronological list of fuel purchases with date filters, liters, amount, fuel type, pump station, slip no | `tabFuel Purchase Entry` via customer session |
| 7 | **Digital Loyalty Card** | `app/(customer)/digital-card.tsx` | Card UI with metallic/petroleum gradient, customer name, vehicle number, dynamic high-contrast QR code for pump scanner | `name` & `qr_access_token` from customer record |
| 8 | **QR Scanner** | `app/(customer)/scanner.tsx` | Expo Camera scanner for pump vouchers, receipts, or staff station check-in | `Expo Camera` + `clp.api.scan_and_process_qr` |
| 9 | **Gifts & Rewards** | `app/(customer)/rewards.tsx` | Filterable reward catalog, point cost badge, stock badge, redemption eligibility status | `clp.api.get_customer_rewards_catalog` |
| 10 | **Gift Redemption** | `app/(customer)/redemption.tsx` | Redemption confirmation modal, point deduction validation, redemption voucher QR, idempotency guard | `clp.api.request_customer_redemption` |
| 11 | **Notifications** | `app/(customer)/notifications.tsx` | Transaction alerts, points credited notifications, redemption receipts, promo alerts | `clp.api.get_customer_notifications` |
| 12 | **Support & Help** | `app/(customer)/support.tsx` | Station directory, helpline numbers, WhatsApp direct chat link, FAQs, Terms | `clp.api.get_whatsapp_link`, static metadata |
| 13 | **Staff Mode (Optional)** | `app/(staff)/...` | Quick sale entry, customer QR lookup, redemption approval for pump operators | `clp.api.create_quick_sale`, `scan_and_process_qr` |

---

## 6. Mobile Application Technology Stack & Design System

### Technology Stack
* **Framework:** React Native with Expo SDK 52
* **Language:** TypeScript 5.x (Strict typing enabled)
* **Routing:** Expo Router v4 (File-based navigation)
* **Network & Data:** Axios + TanStack Query v5 (Caching, automatic re-validation, offline indicators)
* **Form Handling:** React Hook Form + Zod schema validation
* **Secure Storage:** Expo SecureStore (Hardware-backed encrypted storage for tokens)
* **Hardware APIs:** Expo Camera (BarCode / QR scanning), Expo Haptics (Feedback on scan/tap)
* **Styling & UI:** StyleSheet / Tailwind-inspired theme tokens, Lucide React Native icons

### Design System: Premium Petroleum Brand Theme
* **Deep Petroleum Navy:** `#0F172A`
* **Midnight Petrol Blue:** `#1E293B`
* **Primary Fuel Blue:** `#2563EB`
* **Accent Fuel Green:** `#10B981` (Points & Success)
* **Restrained Amber:** `#F59E0B` (Rewards & Alerts)
* **Danger Red:** `#EF4444`
* **Light Slate Background:** `#F8FAFC`
* **Card Surface:** `#FFFFFF` (with soft subtle elevation)
