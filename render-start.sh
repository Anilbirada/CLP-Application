#!/usr/bin/env bash
# ==============================================================================
# Render.com Start Script for Customer Loyalty Program (CLP)
# ==============================================================================
set -o errexit

PORT="${PORT:-10000}"
SITE_NAME="${FRAPPE_SITE_NAME:-clp.localhost}"

echo "==> Starting CLP Application on port ${PORT}..."
echo "==> Bound site: ${SITE_NAME}"

# Ensure python finds all packages
if [ -d "/opt/render/project/src/.venv" ]; then
    export VIRTUAL_ENV="/opt/render/project/src/.venv"
    export PATH="${VIRTUAL_ENV}/bin:${PATH}"
    export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.10/site-packages:${PWD}:${PYTHONPATH}"
fi

# Verify frappe is importable
python -c "import frappe; print('Runtime: Frappe import OK ->', frappe.__file__)"

# Generate site configuration if database credentials exist
mkdir -p "sites/${SITE_NAME}"
cat <<EOF > "sites/${SITE_NAME}/site_config.json"
{
  "db_name": "${DB_NAME:-_3f3c9c84bd5a88ee}",
  "db_password": "${DB_PASSWORD:-U55PDCFtR3UazXQc}",
  "db_type": "mariadb",
  "db_host": "${DB_HOST:-127.0.0.1}",
  "db_port": ${DB_PORT:-3306},
  "redis_cache": "${REDIS_CACHE_URL:-redis://127.0.0.1:6379}",
  "redis_queue": "${REDIS_QUEUE_URL:-redis://127.0.0.1:6379}",
  "developer_mode": 0
}
EOF

mkdir -p "sites"
cat <<EOF > "sites/common_site_config.json"
{
  "webserver_port": ${PORT},
  "auto_update": false
}
EOF

echo "sites/${SITE_NAME}" > "sites/currentsite.txt"

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
    "frappe.app:application"
