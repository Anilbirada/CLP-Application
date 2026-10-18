#!/usr/bin/env bash
# ==============================================================================
# Render.com Build Script for Customer Loyalty Program (CLP)
# ==============================================================================
set -o errexit

echo "==> [1/4] Upgrading Python package managers..."
pip install --upgrade pip setuptools wheel

echo "==> [2/4] Installing Frappe Framework & Gunicorn server..."
pip install frappe-bench "frappe>=15.0.0,<16.0.0" gunicorn werkzeug

echo "==> [3/4] Installing CLP Application dependencies..."
pip install "qrcode[pil]>=7.4,<9" flit_core

echo "==> [4/4] Installing CLP in editable mode..."
pip install -e .

echo "==> Build finished successfully!"
