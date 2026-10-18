# Customer Loyalty Program (CLP) - Application

A full-featured, enterprise-grade **Customer Loyalty & Fuel Management Program (CLP)** built on the **Frappe Framework (v15)** and **MariaDB**.

Designed specifically for petrol pump chains and fuel stations, CLP enables automated customer reward tracking, multi-pump transaction processing, mobile-friendly refuel logging, gift inventory tracking, dynamic role-based security, and customer loyalty dashboards with QR verification.

---

## 🚀 Key Features Implemented (All 6 Phases)

### Phase 1: Registration & Mobile View (Quick Wins)
- **Streamlined Fuel Purchase Interface:** Removed/hidden redundant `fuel_type` field to speed up cashier pump transactions.
- **Mobile Sticky Action Bar:** Added persistent bottom action buttons (`Save & Submit Purchase` and `Next Refuel`) optimized for mobile touchscreens and handheld POS devices.
- **Space-Free & Hyphen-Free Search:** Intelligent vehicle number and mobile search that sanitizes spaces, hyphens, and casing (e.g., searching `MH 45 AX 4507` or `mh-45ax-4507` instantly matches `MH45AX4507`).
- **Vehicle Number Auto-Sanitization:** Auto-cleans leading/trailing/embedded whitespace and converts to uppercase on customer creation.
- **Fast Continuous Refueling:** "Next Refuel" workflow that clears previous vehicle details and prepares the next customer entry in one tap.
- **Multi-Vehicle Support:** Unique index constraints adjusted to permit multiple vehicles per owner or shared family registrations.

### Phase 2: Pump Staff & Security
- **Staff User Role Management:** Dynamic management of CLP staff roles (`Pump Manager`, `CLM Incharge`, `Pump Owner`, `CLP Stock Add`, `CLP Stock Subtract`, `CLP Stock Transfer`, `CLP Reports Viewer`, `CLP Referral Manager`).
- **Staff Activation & Deactivation:** Secure toggling of staff permissions and user accounts with server-side RBAC enforcement.
- **Duplicate Prevention:** Strict server-side validation preventing duplicate active customer registrations by mobile number.
- **Location-Based Tracking:** Ties customer registrations to their specific `Petrol Pump Location`.
- **Exact Date & Time Registration Tracking:** Precise datetime filtering and reporting on customer onboarding.

### Phase 3: Owner Controls & Operations
- **CLP Activity Audit Report:** Detailed audit trail report tracking system activities, logins, balance modifications, and operational events.
- **CLP Customer Balance Adjustment:** Dedicated DocType allowing authorized owners/managers to add or subtract customer points with mandatory audit notes.
- **Gift Item Stock Ledger Report:** End-to-end gift stock movement report logging every addition, deduction, transfer, and redemption with balance tracking.
- **Comprehensive Customer History:** Aggregated transaction logs showing refuels, liters pumped, amounts spent, and gifts redeemed.
- **Audit Logging with Datetime:** Full actor accountability (`modified_by`, `creation`) stored for all mutations.

### Phase 4: Customer Dashboard & QR Verification
- **In-App QR Code Scanner:** Camera-enabled QR scanner with fallback manual space-free search for instant pump lookups.
- **Secure Unguessable QR Access Tokens:** High-entropy 32+ character UUID tokens (`qr_access_token`) ensuring zero enumeration vulnerabilities.
- **Public Customer Points & Schemes Checker:** Responsive web portal at `/loyality/check` allowing customers to view live points, active schemes, and transaction history.
- **Gift Card & Redemption Showcase:** Displays available gift items and points required for redemption.

### Phase 5: Stock Transfer & Inventory Management
- **Pump-to-Pump Stock Transfers:** DocType `Gift Stock Request` with approval workflows for moving gifts between central warehouses and pump stations.
- **Self-Contained Stock Ledger:** Independent stock ledger engine (`clp/stock.py`) and `CLP Gift Stock Ledger` DocType that runs autonomously without requiring ERPNext.
- **Negative Stock & Inconsistency Prevention:** Real-time balance calculations ensuring no pump can issue or transfer more gifts than physically available.
- **Granular Stock Roles:** Segregated permissions (`CLP Stock Add`, `CLP Stock Subtract`, `CLP Stock Transfer`).

### Phase 6: Multi-Pump Analytics & Referral Engine
- **Daily Pump Sales Summary Report:** Script report aggregating daily transactions, total liters dispensed, and gross revenue grouped by petrol pump location.
- **Inactive Customers Report:** Churn detection report identifying customers who haven't refueled in 30, 60, or 90+ days.
- **Customer Referral Engine:** Configurable `CLP Referral Settings` and `Referral Reward Entry` automatically crediting referral points when a referred customer completes their first qualifying refuel.
- **Referral Rewards Report:** Complete overview of all referral rewards awarded across pumps and dates.

---

## 🛠️ Technology Stack

- **Backend Framework:** [Frappe Framework v15](https://frappeframework.com/) (Python 3.10+)
- **Database:** MariaDB 10.6+
- **Frontend:** Frappe Desk (HTML5, CSS3, JavaScript, jQuery, Bootstrap, FontAwesome)
- **Templating:** Jinja2 (SSR public web portal)
- **Scanning:** HTML5 Camera / Barcode & QR Code Scanner API

---

## 📦 Installation & Setup

### 1. Fetch App in Frappe Bench
```bash
cd /path/to/frappe-bench
bench get-app https://github.com/Anilbirada/CLP-Application.git
```

### 2. Install App on Site
```bash
bench --site <your-site-name> install-app clp
```

### 3. Run Database Migrations & Patches
```bash
bench --site <your-site-name> migrate
```

### 4. Build Assets & Restart Bench
```bash
bench build --app clp
bench restart
```

---

## 📄 Key DocTypes & Reports

| Module | Type | Name | Purpose |
| :--- | :--- | :--- | :--- |
| **Customer** | DocType | `Loyalty Customer` | Customer profile, mobile, vehicle number, points balance, and QR token |
| **Transactions** | DocType | `Fuel Purchase Entry` | Mobile-optimized fuel refuel transaction entry |
| **Gifts** | DocType | `Gift Redemption` | Gift redemption transactions and points deductions |
| **Stock** | DocType | `CLP Gift Stock Ledger` | Independent gift inventory ledger across pump locations |
| **Transfers** | DocType | `Gift Stock Request` | Multi-pump stock movement request & approval workflow |
| **Owner Adjustments**| DocType | `CLP Customer Balance Adjustment` | Owner manual point balance adjustment with required reason notes |
| **Referrals** | DocType | `Referral Reward Entry` | Referral reward tracking engine |
| **Reports** | Script Report | `Daily Pump Sales Summary` | Daily aggregated liters and revenue per pump |
| **Reports** | Script Report | `Inactive Customers Report` | Churn tracking for customers inactive over N days |
| **Reports** | Script Report | `Gift Item Stock Ledger Report`| Gift stock in/out audit ledger |
| **Reports** | Script Report | `CLP Activity Audit Report` | System-wide audit log for all user actions |
| **Reports** | Script Report | `Referral Rewards Report` | Overview of referral bonuses and status |

---

## 🔒 Security & Privacy

- **Server-Side Role Enforcements:** API calls strictly validated against user session roles using `set(frappe.get_roles()) & allowed_roles`.
- **Private Data Protection:** Customer phone numbers are masked on public QR endpoints.
- **Unguessable Tokens:** Public QR lookup requires 32+ character cryptographic tokens, preventing unauthorized record enumeration.

---

## 📝 License

Distributed under the MIT License.
