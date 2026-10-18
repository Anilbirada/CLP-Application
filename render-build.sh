#!/usr/bin/env bash
# ==============================================================================
# Render.com Build Script for Customer Loyalty Program (CLP)
# ==============================================================================
set -o errexit

echo "==> [1/4] Upgrading Python package managers..."
pip install --upgrade pip setuptools wheel

echo "==> [2/4] Installing Frappe Framework v15 & Gunicorn..."
FRAPPE_DIR="${HOME}/frappe-framework"
if [ ! -d "${FRAPPE_DIR}" ]; then
    echo "Cloning Frappe Framework (version-15)..."
    git clone --depth 1 --branch version-15 https://github.com/frappe/frappe.git "${FRAPPE_DIR}"
fi
pip install -e "${FRAPPE_DIR}"
pip install gunicorn werkzeug

echo "==> [3/4] Installing CLP Application dependencies..."
pip install "qrcode[pil]>=7.4,<9" flit_core

echo "==> [4/4] Installing CLP in editable mode..."
pip install -e .

echo "==> Build finished successfully!"
