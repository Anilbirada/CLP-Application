# CLP Mobile Application – API Integration Specification
## Authoritative Endpoints, Contracts, Schemas & Error Models

**Base Production URL:** `https://clp.hiideals.com`  
**Base Development URL:** `http://localhost:8000` or Cloudflare Tunnel Edge  
**Authentication Paradigms:**
1. **Customer Token Session:** 32-byte cryptographically secure token (`qr_access_token`) issued upon mobile verification and stored in hardware-backed `Expo SecureStore`.
2. **Staff / Desk Session:** Standard Frappe session cookie (`sid`) or HTTP header via `/api/method/login`.

---

## 1. Authentication & Session APIs

### 1.1 Customer Mobile Login & Verification
* **Endpoint:** `/api/method/clp.api.customer_mobile_login`
* **HTTP Method:** `POST` or `GET`
* **Authentication:** None (Public / Guest Whitelisted)
* **Rate Limit:** 20 requests per 60 seconds per IP
* **Purpose:** Authenticates customer by registered 10-digit mobile number or vehicle number. Validates that the customer is `Active`. Returns the customer profile and secure persistent session token (`qr_access_token`).
* **Request Parameters:**
  ```json
  {
    "identifier": "9876543210" // 10-digit mobile or uppercase vehicle number (e.g. KA01AB1234)
  }
  ```
* **Success Response (`200 OK`):**
  ```json
  {
    "message": {
      "success": true,
      "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
      "customer": {
        "name": "CUST-00123",
        "customer_name": "Rajesh Kumar",
        "mobile_number": "9876543210",
        "vehicle_number": "KA01AB1234",
        "current_cycle_liters": 145.5,
        "total_liters_purchased": 1280.0,
        "total_gifts_received": 3,
        "referral_points_balance": 40.0,
        "registration_date": "2025-06-12",
        "qr_access_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
      }
    }
  }
  ```
* **Error Responses:**
  * `404 Not Found`:
    ```json
    { "exc_type": "DoesNotExistError", "message": "No customer found matching provided mobile or vehicle number. Please visit a pump to register." }
    ```
  * `403 Forbidden`:
    ```json
    { "exc_type": "PermissionError", "message": "Customer account is currently inactive. Please contact station support." }
    ```
  * `429 Too Many Requests`:
    ```json
    { "message": "Too Many Requests. Try again in 60 seconds." }
    ```

---

### 1.2 Customer Session Re-validation by Token
* **Endpoint:** `/api/method/clp.api.get_customer_portal_by_token`
* **HTTP Method:** `GET`
* **Authentication:** None (Whitelisted via secure token)
* **Purpose:** Called on mobile app launch or pull-to-refresh to revalidate session, fetch latest authoritative balance, and retrieve recent transactions.
* **Request Query Parameters:**
  `?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`
* **Success Response (`200 OK`):**
  ```json
  {
    "message": {
      "found": true,
      "customer": {
        "name": "CUST-00123",
        "customer_name": "Rajesh Kumar",
        "mobile_number": "******3210",
        "vehicle_number": "KA01AB1234",
        "registration_date": "2025-06-12",
        "current_cycle_liters": 145.5,
        "total_liters_purchased": 1280.0,
        "total_gifts_received": 3,
        "referral_points_balance": 40.0
      },
      "purchases": [
        {
          "name": "FPE-2026-00412",
          "purchase_date": "2026-10-25 14:30:00",
          "petrol_pump": "Sindol Petroleum Pump 1",
          "liters": 35.0,
          "amount": 3550.0,
          "fuel_type": "Petrol",
          "slip_no": "SLP-8921"
        }
      ],
      "redemptions": [
        {
          "name": "RED-2026-00089",
          "redemption_date": "2026-09-18 11:20:00",
          "petrol_pump": "Sindol Petroleum Pump 1",
          "total_points": 100.0,
          "items": [
            {
              "gift_item": "GIFT-FLASK",
              "item_name": "Insulated Steel Flask 1L",
              "points_required": 100.0
            }
          ]
        }
      ]
    }
  }
  ```
* **Error Response (`403 Forbidden`):**
  ```json
  { "exc_type": "PermissionError", "message": "Invalid or expired customer access token" }
  ```

---

### 1.3 Staff Credentials Login (Optional Staff Mode)
* **Endpoint:** `/api/method/login`
* **HTTP Method:** `POST`
* **Authentication:** Basic / Form
* **Parameters:**
  ```json
  {
    "usr": "operator1@hiideals.com",
    "pwd": "secure_password"
  }
  ```
* **Success Response (`200 OK`):**
  Sets `sid` HTTP-only cookie and returns user details.
* **Error Response (`401 Unauthorized`):** Invalid credentials.

---

## 2. Loyalty Points & Transaction History APIs

### 2.1 Public Loyalty Status & Multi-Parameter Check
* **Endpoint:** `/api/method/clp.api.check_loyalty_points`
* **HTTP Method:** `GET` or `POST`
* **Authentication:** None (Public / Guest Whitelisted)
* **Rate Limit:** 30 req / 60s
* **Query Parameters:**
  * `vehicle` (optional string): Vehicle registration number
  * `mobile` (optional string): 10-digit mobile number
* **Success Response (`200 OK`):**
  Returns `{ found: true, customer: {...}, purchases: [...], redemptions: [...] }`
* **Error Response:**
  `{ found: false, error: "No customer found matching vehicle '...'" }`

---

## 3. Rewards & Gift Catalog APIs

### 3.1 Customer Rewards Catalog
* **Endpoint:** `/api/method/clp.api.get_customer_rewards_catalog`
* **HTTP Method:** `GET`
* **Authentication:** None (Public Whitelisted)
* **Parameters:**
  * `petrol_pump` (optional string): Filter catalog for a specific station
* **Success Response (`200 OK`):**
  ```json
  {
    "message": [
      {
        "gift_item": "GIFT-FLASK",
        "item_name": "Insulated Stainless Steel Flask 1L",
        "points_required": 100.0,
        "description": "High durability double-wall vacuum insulated water bottle.",
        "petrol_pump": "Sindol Petroleum Pump 1",
        "pump_name": "N.K. Sindol Petroleum - Station 1",
        "in_stock": true,
        "stock_qty": 24.0
      },
      {
        "gift_item": "GIFT-HELMET",
        "item_name": "ISI Certified Riding Helmet",
        "points_required": 250.0,
        "description": "Premium safety helmet for two-wheelers.",
        "petrol_pump": "Sindol Petroleum Pump 1",
        "pump_name": "N.K. Sindol Petroleum - Station 1",
        "in_stock": true,
        "stock_qty": 12.0
      }
    ]
  }
  ```

---

## 4. Notifications & Activity Feed APIs

### 4.1 Chronological Customer Activity Stream
* **Endpoint:** `/api/method/clp.api.get_customer_notifications`
* **HTTP Method:** `GET`
* **Authentication:** Customer Token
* **Parameters:**
  * `token` (string, required): 32-byte customer token
* **Success Response (`200 OK`):**
  ```json
  {
    "message": [
      {
        "id": "fuel-FPE-2026-00412",
        "type": "fuel_purchase",
        "title": "Fuel Points Credited: +35.0L",
        "message": "Purchased 35.0L Petrol at Sindol Petroleum Pump 1. Total ₹3550.0.",
        "timestamp": "2026-10-25 14:30:00",
        "read": false
      },
      {
        "id": "gift-RED-2026-00089",
        "type": "gift_redemption",
        "title": "Reward Redeemed: -100.0L",
        "message": "Successfully claimed reward at Sindol Petroleum Pump 1.",
        "timestamp": "2026-09-18 11:20:00",
        "read": true
      },
      {
        "id": "ref-REF-00042",
        "type": "referral_bonus",
        "title": "Referral Bonus Credited: +20 pts",
        "message": "A friend you referred completed their first fuel purchase!",
        "timestamp": "2026-09-10 16:45:00",
        "read": false
      }
    ]
  }
  ```

---

## 5. Profile Management APIs

### 5.1 Update Customer Profile
* **Endpoint:** `/api/method/clp.api.update_customer_profile`
* **HTTP Method:** `POST`
* **Authentication:** Customer Token
* **Parameters:**
  ```json
  {
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
    "customer_name": "Rajesh Kumar",
    "vehicle_number": "KA01AB1234"
  }
  ```
* **Success Response (`200 OK`):**
  ```json
  {
    "message": {
      "success": true,
      "message": "Profile updated successfully",
      "customer": {
        "name": "CUST-00123",
        "customer_name": "Rajesh Kumar",
        "vehicle_number": "KA01AB1234",
        "mobile_number": "9876543210",
        "current_cycle_liters": 145.5,
        "total_liters_purchased": 1280.0,
        "total_gifts_received": 3
      }
    }
  }
  ```

---

## 6. Support & Pump Contact APIs

### 6.1 Direct WhatsApp Support Generator
* **Endpoint:** `/api/method/clp.api.get_whatsapp_link`
* **HTTP Method:** `GET`
* **Parameters:**
  * `customer_id` (string): Customer ID
  * `pump_name` (optional string): Pump Station name
* **Success Response (`200 OK`):**
  Returns `{ message: "https://api.whatsapp.com/send?phone=...&text=..." }`
