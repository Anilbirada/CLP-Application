# CLP Existing-App Enhancement Package

This package modifies the original Frappe-based CLP application. It does not replace it with a new stack.

## Changes included

- Added customer referrer, referral-points balance, QR access token and registration petrol-pump fields.
- Removed the vehicle-number uniqueness rule from the DocType and customer validation; added a post-model-sync patch to remove an existing standalone unique index if present.
- Kept the customer mobile number unique and normalized vehicle/mobile input.
- Hid the fuel-type field from the Fuel Purchase Entry form while preserving the legacy field for historical compatibility.
- Added exact date/time registration Script Report with optional registration-pump filter.
- Added referral reward settings, referral reward ledger, referral rewards Script Report and points award on submitted eligible fuel purchases.
- Reverses referral points when the related fuel purchase is cancelled.
- Added customer-specific high-entropy QR token URLs and a public token-based portal API; the existing public manual lookup now requires both vehicle number and mobile number.
- Added customer mobile/vehicle/driver fields to Gift Redemption for issue traceability.
- Added custom CLP roles for stock add, stock subtract, stock transfer, reports and referral management.
- Added owner-managed role assignment button to the standard Frappe User form and server-side role checks for stock adjustment/transfer.
- Added CLP Activity Log DocType and document event hooks for customer, fuel, gift, stock, user and referral changes.

## Apply on a development/staging site first

1. Back up the site and database.
2. Copy the updated `clp` app folder into the existing Bench `apps/clp/clp` location (or replace the app source from this package while preserving local uncommitted work).
3. From the Bench directory, run:

   ```bash
   bench --site <your-site-name> migrate
   bench --site <your-site-name> clear-cache
   bench build --app clp
   bench restart
   ```

4. Open **CLP Referral Settings** and enable referral rewards; configure points per eligible purchase and optional minimum amount.
5. Assign roles using the **Manage CLP Roles** button on the User form. Verify each restricted API with a test user.
6. Test registrations, duplicate vehicle handling, unique mobile validation, exact date/time report, QR portal, gift issue details, stock add/subtract/transfer, referral reward award and cancellation reversal.

## Important verification notes

- This source package has been syntax-checked and its JSON files parsed. It has not been run against your live Frappe site or production database in this environment.
- Run on staging first and inspect migration output before production rollout.
- Existing historical customer records will not automatically gain a registration pump; the field will be available for new registrations. Historical pump-wise reporting requires reliable source data for backfill.
- QR links are bearer-token links and currently do not have an expiry timestamp/OTP challenge. Protect them as private links and add expiry/OTP if required by the business/security policy.
- The referral rule is configurable for points per submitted fuel purchase and minimum amount. Confirm whether rewards should be limited by time, pump, purchase value, or total number before enabling it for real customers.
- The original customer request to “add/subtract notes” is ambiguous. No monetary/loyalty balance adjustment workflow has been invented; clarify whether this means cash credit, loyalty points, or a text note before implementing it.
- This package adds the registration-time and referral reports while preserving the existing reports. “As many reports as possible” should be prioritized against the data actually available in CLP and any connected sales/accounting system.
