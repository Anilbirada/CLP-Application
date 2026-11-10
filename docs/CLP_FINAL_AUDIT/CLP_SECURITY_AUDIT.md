# CLP Customer Loyalty Program – Cybersecurity & Access Control Audit

**Target Production Domain:** `https://clp.hiideals.com`  
**Base Commit:** `0f66021` | **Audit Branch:** `feat/final-audit-verification`  
**Date:** November 10, 2026  
**Auditor:** Senior Application Security & Architecture Engineer  

---

## 1. Security Architecture & Threat Model Overview

The CLP system handles customer personally identifiable information (PII), loyalty points with real economic value (redeemable for physical gifts), and inventory balances. The security audit evaluated threat vectors across public guest interfaces, attendant scanning tools, internal desk forms, and background jobs.

---

## 2. Security Controls & Penetration Test Findings

| Threat / Vulnerability Area | Attack Vector | Security Control Implemented | Verification Result | Status |
| :--- | :--- | :--- | :---: | :---: |
| **Customer Phone Enumeration** | Automated scraping of phone numbers via `/api/method/clp.api.check_loyalty_points`. | Masking applied to guest responses: returns `******1234` and `Rahul S.***`. Strict IP rate limit: 30 requests / 60 seconds. | Direct cURL requests as Guest verified phone numbers are masked. | **PASSED** |
| **Privilege Escalation** | Staff user attempting to assign themselves `Pump Owner` or `System Manager`. | `clp.api.create_staff_account` strictly limits selectable roles to staff tiers unless caller is already `System Manager`. Direct user role modifications restricted. | Calling `create_staff_account` as non-owner returns HTTP 403 `PermissionError`. | **PASSED** |
| **Unauthorized Stock Adjustment** | Frontline attendant adjusting inventory via API. | Backend check in `clp.api.adjust_gift_stock` verifies `_has_role("System Manager") or _has_role("Pump Owner")`. | Invoking API as attendant or guest is immediately rejected. | **PASSED** |
| **QR Code Tampering & Spoofing** | Guessing sequential customer IDs in QR URLs. | QR codes encode cryptographically secure 32-character tokens (`secrets.token_urlsafe(32)` $\approx 256$ bits of entropy). Sequential guessing is mathematically infeasible. | Generated QR URLs carry high-entropy token query parameters. | **PASSED** |
| **Session Revocation on Deactivation** | Deactivated staff user continuing to use existing sessions. | `clp.api.deactivate_staff_account` sets `tabUser.enabled = 0` and `tabUser Pump Settings.is_active = 0`. Frappe session validation terminates disabled accounts on next request. | Deactivated user cannot submit transactions or authenticate. | **PASSED** |
| **Audit Log PII & Secret Leakage** | Storing customer passwords, tokens, or auth cookies in `tabCLP Activity Log`. | `clp.audit.log_doc_event` sanitizes payloads, capturing only document status, liters, points, and pump name. Password and token fields are excluded. | Inspected `tabCLP Activity Log` records; zero secrets or tokens stored. | **PASSED** |
| **Cross-Pump Data Leakage** | Attendant at Pump A accessing restricted stock or settings of Pump B. | User Pump Settings locks attendants to their assigned pump. `get_user_default_pump` resolves strictly from the authenticated session user. | Pump scoping verified across attendant forms. | **PASSED** |
| **SQL Injection** | SQL injection via search boxes or vehicle queries. | All raw database interactions utilize parameterized queries (`%(param)s` and tuple bindings) with strict regex sanitization. | Automated tests with SQL injection strings safely escaped. | **PASSED** |

---

## 3. Cryptographic Token Generation Specification

In [`loyalty_customer.py`](file:///E:/clp%20updated%20code/clp-code-reviewed-fixed-1/clp-develop/clp/customer_loyality_program/doctype/loyalty_customer/loyalty_customer.py):
```python
if not self.qr_access_token:
    self.qr_access_token = secrets.token_urlsafe(32)
```
- **Randomness Source:** Operating system cryptographically secure pseudorandom number generator (`os.urandom`).
- **Entropy:** 32 bytes $\times 8 = 256$ bits of cryptographic entropy.
- **Collision Probability:** $< 10^{-30}$, eliminating collision and token enumeration risks.

---

## 4. Rate Limiting Configuration

Applied to all public endpoints:
```python
@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60, ip_based=True)
def check_loyalty_points(vehicle=None, mobile=None, token=None):
```
- Stored and tracked in Redis cache (`redis_cache`).
- Exceeding 30 requests in 60 seconds returns HTTP 429 Too Many Requests.
- Protects MariaDB against Denial of Service (DoS) and brute-force scans.

---

## 5. Security Audit Verdict

The CLP application implements strong defense-in-depth principles. PII exposure risks are eliminated, role boundaries are enforced server-side, and administrative RPCs are strictly guarded.
