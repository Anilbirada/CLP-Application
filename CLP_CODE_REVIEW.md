# CLP Code Review and Static Validation

Review date: 16 October 2026

## High-risk issues corrected in this revision

1. **Stored XSS in the public loyalty page** — database/API values were interpolated directly into `innerHTML`. Dynamic values are now HTML-escaped before insertion.
2. **SQL injection in gift-stock filtering** — pump and item filters are now bound SQL parameters, not concatenated into SQL.
3. **Customer-data API access** — staff-facing customer search/lookup, QR scan, dashboard, stock, report, and WhatsApp endpoints now require an appropriate CLP role; stock-only roles are excluded from customer PII lookup.
4. **QR generation endpoint** — bulk QR generation is owner/admin-only, validates and caps inputs, supports the app's prefixed customer IDs, writes no arbitrary server paths, and returns a private ZIP file URL.
5. **Role-management regression** — the CLP role dialog no longer strips an existing `System Manager` role when saving CLP roles. The endpoint cannot assign `System Manager` through this UI.
6. **Transaction integrity** — removed explicit database commits from document hooks / user pump settings so Frappe can roll back failed operations.
7. **Fuel purchase lifecycle** — loyalty litres are now applied on submit, not on draft insertion; cancellation reverses the submitted transaction. Null-safe balance arithmetic and negative-amount validation were added.
8. **Gift redemption validation** — the warehouse must match the selected pump; gift points and item names are read from pump configuration rather than trusted from the client; duplicate rows for one gift are checked against aggregate stock demand; customer mobile and vehicle are copied to the redemption for traceability; null-safe balance updates were added.
9. **Stock transfer validation** — positive quantity, distinct warehouses, pump-to-warehouse mapping, and source stock availability are validated before submission.
10. **Duplicate DocType field definitions** — duplicate `amended_from` field definitions were removed from Fuel Purchase Entry and Gift Redemption.
11. **Input and report validation** — numeric inputs, stock-status filters, report date ranges and query limits are validated; referral balance increments/decrements use atomic SQL updates.
12. **Public manual lookup** — removed the unnecessary CSRF bypass flag. Manual lookup still requires both vehicle and mobile identifiers; QR access remains token-based.

## Static checks completed

- Python syntax/AST parse: all 64 Python files passed.
- JavaScript syntax: all app JavaScript files passed `node --check`.
- Public loyalty page inline JavaScript: passed `node --check`.
- JSON parse and DocType field-name uniqueness: all 32 JSON files passed; no duplicate field names remain.
- ZIP integrity: will be checked on the final archive.

## Important tests not completed

This environment does **not** have the Frappe Python package, a Bench site, Redis, or a MariaDB instance installed. Therefore the following are **not certified** here:

- `bench --site <site> migrate` / DocType schema synchronization
- Installing the app into a clean Frappe site
- Real Frappe permission enforcement and lifecycle hooks
- ERPNext Stock Entry creation/submission/cancellation against a real company, warehouse and stock ledger
- Browser/UI end-to-end tests and concurrent transaction tests
- Full verification of every business requirement and existing production-data migration

The repository's existing `FrappeTestCase` classes are empty placeholders; they do not provide meaningful automated functional coverage yet. Do not deploy this archive directly to production without a staging install and real workflow tests.

## Known business/security decisions still requiring validation

- The QR portal is a bearer-token link: anyone holding the QR/link can view that customer's available history. Token expiry/rotation and rate limiting are not implemented.
- The public manual lookup relies on knowledge of both vehicle and mobile number and has no application-level rate limit; consider throttling and monitoring before public deployment.
- Referral rewards are awarded per qualifying submitted purchase, according to configured points/minimum amount. Business rules for maximum rewards, referral expiry, refund/partial reversal, and abuse prevention have not been specified.
- The request to add/subtract “notes” remains ambiguous (text note vs. loyalty points vs. monetary balance) and was not invented as a financial workflow.
- Existing customer records cannot be reliably assigned a historical registration pump unless source data exists for backfill.
- This remains a Frappe app and must run inside a compatible Frappe/Bench + MariaDB/Redis environment; it is not a standalone desktop application.
