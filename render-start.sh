#!/usr/bin/env bash
# ==============================================================================
# Render.com Start Script for Customer Loyalty Program (CLP)
# ==============================================================================
set -o errexit

PORT="${PORT:-10000}"
SITE_NAME="${FRAPPE_SITE_NAME:-clp.localhost}"

echo "==> Starting CLP Application on port ${PORT}..."
echo "==> Bound site: ${SITE_NAME}"

# Export site name for Frappe single-tenant WSGI routing
export FRAPPE_SITE="${SITE_NAME}"

# Launch production Gunicorn WSGI server
exec gunicorn \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --preload \
    "frappe.app:application"
