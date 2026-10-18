#!/usr/bin/env bash
# ==============================================================================
# Render.com Build Script for Customer Loyalty Program (CLP)
# ==============================================================================
set -o errexit

echo "==> [1/4] Upgrading Python package managers..."
pip install --upgrade pip setuptools wheel

echo "==> [2/4] Cloning & Installing Frappe Framework into site-packages..."
FRAPPE_DIR="./frappe-framework"
if [ ! -d "${FRAPPE_DIR}" ]; then
    echo "Cloning Frappe Framework (version-15)..."
    git clone --depth 1 --branch version-15 https://github.com/frappe/frappe.git "${FRAPPE_DIR}"
fi

# Install Frappe as a standalone package into .venv (NO editable -e mode!)
pip install "${FRAPPE_DIR}"
pip install gunicorn werkzeug

echo "==> [3/4] Installing CLP Application dependencies..."
pip install "qrcode[pil]>=7.4,<9" flit_core

echo "==> [4/4] Installing CLP into site-packages..."
pip install .

echo "==> Verifying frappe installation..."
python -c "import frappe; print('Frappe successfully imported from:', frappe.__file__)"

echo "==> Build finished successfully!"
