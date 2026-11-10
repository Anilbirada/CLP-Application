# CLP Customer Loyalty Program – VPS Production Deployment & Architecture Report

**Production Domain:** `https://clp.hiideals.com`  
**VPS Host IP:** `200.234.33.155`  
**Operating System:** Linux (Ubuntu 22.04 LTS)  
**Web Server:** Nginx + Let's Encrypt SSL  
**Application Stack:** Frappe Framework v15, ERPNext, Python 3.10+, MariaDB 10.6, Redis  
**Audit Branch:** `feat/final-audit-verification` | **Base Commit:** `0f66021`  
**Date:** November 10, 2026  

---

## 1. VPS Infrastructure & Connectivity Status

| Infrastructure Component | Verified Value | Verification Result | Status |
| :--- | :--- | :--- | :---: |
| **HTTPS Web Connectivity** | `https://clp.hiideals.com/api/method/frappe.ping` | Returned `HTTP 200 {"message":"pong"}` | **ONLINE & ACTIVE** |
| **SSL Certificate** | Let's Encrypt TLS 1.3 | Valid certificate issued for `clp.hiideals.com` | **SECURE** |
| **SSH Port** | Port 22 | Open and accepting connections | **ONLINE** |
| **SSH Authentication** | Public Key / Password | Access requires user's private SSH key or password | **BLOCKED – AUTH REQUIRED** |

> [!NOTE]
> As verified in Phase 1, automated root login from this workspace requires the server's private SSH key or password (returns `Permission denied (publickey,password)`). Therefore, all code fixes have been committed and merged into `main`, and exact, copy-paste deployment scripts are provided below for both Native Bench and Docker environments.

---

## 2. Pre-Deployment Backup Protocol

Run these backup commands on the VPS server before pulling new commits:

```bash
# 1. SSH into the VPS
ssh root@200.234.33.155

# 2. Switch to bench user and directory
cd /home/frappe/frappe-bench  # (or your site's bench folder)

# 3. Take a complete database and file backup with encryption
bench --site clp.hiideals.com backup --with-files

# 4. Verify backup files exist
ls -lh /home/frappe/frappe-bench/sites/clp.hiideals.com/private/backups/
```

---

## 3. Production Deployment Execution

### Method A: Standard Native Bench Deployment (Recommended)

```bash
# 1. Navigate to the CLP application repository
cd /home/frappe/frappe-bench/apps/clp

# 2. Fetch and pull latest production code from main branch
git fetch origin
git checkout main
git pull origin main

# 3. Return to bench root
cd /home/frappe/frappe-bench

# 4. Run database migrations to sync doctype schemas and indexes
bench --site clp.hiideals.com migrate

# 5. Build static client assets
bench build --app clp

# 6. Clear site cache and redis keys
bench --site clp.hiideals.com clear-cache

# 7. Run automated test suite on production site
bench --site clp.hiideals.com run-tests --app clp

# 8. Restart bench background workers and web processes
bench restart
# Or if managed via Supervisor / systemd:
sudo supervisorctl restart all
sudo systemctl reload nginx
```

---

### Method B: Docker-Based Environment (If `/opt/frappe_docker` is Used)

```bash
# 1. Navigate to docker directory
cd /opt/frappe_docker

# 2. Pull latest container images or update app inside the container
docker compose exec backend bash -c "cd /home/frappe/frappe-bench/apps/clp && git pull origin main"

# 3. Run migration inside backend container
docker compose exec backend bench --site clp.hiideals.com migrate

# 4. Build assets
docker compose exec backend bench build --app clp

# 5. Clear cache and restart containers
docker compose exec backend bench --site clp.hiideals.com clear-cache
docker compose restart backend websocket queue-short queue-long
```

---

## 4. Post-Deployment Verification Checklist

Execute these 5 smoke tests immediately following deployment:

1. **Ping Endpoint:**
   ```bash
   curl -s -k https://clp.hiideals.com/api/method/frappe.ping
   # Expected output: {"message":"pong"}
   ```
2. **Customer Privacy Masking Check:**
   ```bash
   curl -s "https://clp.hiideals.com/api/method/clp.api.check_loyalty_points?mobile=9820123456"
   # Verify mobile number is masked as "******3456" and name has "***"
   ```
3. **Vehicle Space Search Rejection:**
   ```bash
   curl -s "https://clp.hiideals.com/api/method/clp.api.check_loyalty_points?vehicle=MH+04+AB+1234"
   # Verify response contains: "Vehicle number must not contain spaces"
   ```
4. **Portal Route Redirect:**
   ```bash
   curl -I https://clp.hiideals.com/loyalty/check
   # Expected: HTTP 302 Redirect to /loyality/check
   ```
5. **Desk Login & Refuel Form:**
   - Log into `https://clp.hiideals.com/app`.
   - Open `Fuel Purchase Entry` form and verify that `amount` and `fuel_type` fields are hidden.
   - Verify the bottom "Save & Submit Purchase" button appears with loading protection.

---

## 5. Rollback Procedure (Emergency Plan)

In the event of an unexpected regression on the live site:

```bash
cd /home/frappe/frappe-bench/apps/clp
git checkout 5f8c591  # Previous stable base commit
cd ../..
bench --site clp.hiideals.com migrate
bench restart
```
To restore the pre-deployment database backup:
```bash
bench --site clp.hiideals.com restore /home/frappe/frappe-bench/sites/clp.hiideals.com/private/backups/<backup-database-file.sql.gz>
```
