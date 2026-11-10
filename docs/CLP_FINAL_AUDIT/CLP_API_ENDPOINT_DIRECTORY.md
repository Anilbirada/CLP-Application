# CLP Customer Loyalty Program – API Endpoint Technical Specification

**Target Production Domain:** `https://clp.hiideals.com`  
**API Protocol:** HTTPS / JSON REST  
**Authentication Types:** Frappe Session Cookies (`sid`), API Key/Secret (`token <api_key>:<api_secret>`), or Public Guest  
**Base Commit:** `0f66021` | **Audit Branch:** `feat/final-audit-verification`  

---

## 1. Authentication & Session APIs

### 1.1 User Login
- **Endpoint:** `POST https://clp.hiideals.com/api/method/login`
- **Auth:** Public
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "usr": "staff@example.com",
    "pwd": "StaffPassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Logged In",
    "home_page": "/app",
    "full_name": "Attendant Name"
  }
  ```
- **Cookies Set:** `sid=<session_id>; Path=/; HttpOnly; Secure; SameSite=Lax`

### 1.2 User Logout
- **Endpoint:** `POST https://clp.hiideals.com/api/method/logout`
- **Auth:** Authenticated User
- **Response:** `{"message": "Logged Out"}`

---

## 2. Customer & Loyalty Query APIs

### 2.1 Check Customer Loyalty Points (Public & Tokenized)
- **Endpoint:** `GET /api/method/clp.api.check_loyalty_points`
- **Auth:** Public (`allow_guest=True`)
- **Rate Limit:** 30 requests / 60 seconds per IP
- **Query Parameters:**
  - `vehicle` (optional): Vehicle number (e.g., `MH04GF6292`). Spaces are rejected.
  - `mobile` (optional): 10-digit mobile number.
  - `token` (optional): Customer 32-character URL-safe QR access token.
- **Example Guest Request:**
  `GET /api/method/clp.api.check_loyalty_points?mobile=9820123456`
- **Response (Masked):**
  ```json
  {
    "message": {
      "found": true,
      "customer": {
        "name": "MANUAL-0001",
        "customer_name": "Ramesh S.***",
        "vehicle_number": "MH04AB1234",
        "mobile_number": "******3456",
        "current_cycle_liters": 65.5,
        "total_liters_purchased": 210.0,
        "total_gifts_received": 1,
        "registration_date": "2026-01-15"
      },
      "purchases": [
        {
          "purchase_date": "2026-11-08 14:22:00",
          "liters": 45.0,
          "amount": 4500.0,
          "fuel_type": "Fuel",
          "petrol_pump": "Main Highway Station"
        }
      ],
      "redemptions": []
    }
  }
  ```

### 2.2 Scan & Process QR (Staff Attendant Scanner)
- **Endpoint:** `POST /api/method/clp.api.scan_and_process_qr`
- **Auth:** Staff (`System Manager`, `Pump Owner`, `Pump Manager`, `CLM Incharge`)
- **Request Body:**
  ```json
  {
    "qr_data": "https://clp.hiideals.com/loyality/check?token=aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"
  }
  ```
- **Response:**
  ```json
  {
    "message": {
      "exists": true,
      "customer_id": "MANUAL-0001",
      "customer_name": "Ramesh Sharma",
      "vehicle_number": "MH04AB1234",
      "mobile_number": "9820123456",
      "current_cycle_liters": 65.5,
      "total_gifts_received": 1
    }
  }
  ```

### 2.3 Search Customer for Scanner Dialog
- **Endpoint:** `POST /api/method/clp.api.search_customer_for_scanner`
- **Auth:** Staff
- **Request Body:** `{"search_text": "MH04"}`
- **Response:** Array of matched active customers sorted by relevance.

---

## 3. Fuel Purchase Transaction APIs

### 3.1 Submit Fuel Purchase Entry
- **Endpoint:** `POST /api/method/frappe.client.insert`
- **Auth:** Staff (`CLM Incharge`, `Pump Manager`, `Pump Owner`)
- **Request Body:**
  ```json
  {
    "doc": {
      "doctype": "Fuel Purchase Entry",
      "petrol_pump": "Main Highway Station",
      "customer": "MANUAL-0001",
      "liters": 50.0,
      "purchase_date": "2026-11-10 12:00:00"
    }
  }
  ```
- **Followed by Submit:** `POST /api/method/frappe.client.submit` with `doc: {...}`
- **Effect:** Increments customer's `current_cycle_liters` and `total_liters_purchased` by 50.0L.

---

## 4. Gift Inventory & Redemption APIs

### 4.1 Adjust Gift Stock (Owner-Only)
- **Endpoint:** `POST /api/method/clp.api.adjust_gift_stock`
- **Auth:** Owner (`Pump Owner`, `System Manager`)
- **Request Body:**
  ```json
  {
    "item_code": "GIFT-WATCH-01",
    "warehouse": "Stores - NK",
    "qty": 10.0,
    "action": "add",
    "reason": "Stock Purchase Restock"
  }
  ```
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "item_code": "GIFT-WATCH-01",
      "actual_qty": 35.0,
      "warehouse": "Stores - NK"
    }
  }
  ```

### 4.2 Submit Gift Redemption
- **Endpoint:** `POST /api/method/frappe.client.insert`
- **Auth:** Staff
- **Request Body:**
  ```json
  {
    "doc": {
      "doctype": "Gift Redemption",
      "customer": "MANUAL-0001",
      "petrol_pump": "Main Highway Station",
      "warehouse": "Stores - NK",
      "items": [
        {
          "gift_item": "GIFT-WATCH-01",
          "points_required": 40.0
        }
      ]
    }
  }
  ```
- **Followed by Submit:** `POST /api/method/frappe.client.submit`
- **Effect:** Deducts 40.0 points from customer cycle balance, creates ERPNext Material Issue, logs CLP Gift Stock Ledger entry with `skip_bin_sync=True`.

---

## 5. Staff Administration APIs (Owner-Only)

### 5.1 Create Staff Account
- **Endpoint:** `POST /api/method/clp.api.create_staff_account`
- **Auth:** Owner (`Pump Owner`, `System Manager`)
- **Request Body:**
  ```json
  {
    "email": "attendant1@hiideals.com",
    "first_name": "Sanjay",
    "last_name": "Patil",
    "mobile_no": "9820000001",
    "pump": "Main Highway Station",
    "role": "CLM Incharge"
  }
  ```
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "message": "Staff account attendant1@hiideals.com created/updated successfully.",
      "user": "attendant1@hiideals.com",
      "role": "CLM Incharge",
      "pump": "Main Highway Station",
      "is_new": true
    }
  }
  ```

### 5.2 Deactivate Staff Account
- **Endpoint:** `POST /api/method/clp.api.deactivate_staff_account`
- **Auth:** Owner (`Pump Owner`, `System Manager`)
- **Request Body:**
  ```json
  {
    "user_id": "attendant1@hiideals.com"
  }
  ```
- **Response:**
  ```json
  {
    "message": {
      "success": true,
      "message": "Staff account attendant1@hiideals.com has been deactivated."
    }
  }
  ```

### 5.3 Get Staff Directory
- **Endpoint:** `GET /api/method/clp.api.get_staff_list`
- **Auth:** Owner (`Pump Owner`, `System Manager`)
- **Query Parameter:** `petrol_pump` (optional filter)
- **Response:** Array of user records, roles, default pumps, and active statuses.
