# ==============================================================================
# Dockerfile for Customer Loyalty Program (CLP) on Render.com
# ==============================================================================
FROM python:3.10-slim-bullseye

# System dependencies for MariaDB client, Pillow, and Frappe
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Frappe & Gunicorn
RUN pip install --no-cache-dir "frappe>=15.0.0,<16.0.0" gunicorn "qrcode[pil]>=7.4,<9" flit_core

# Copy CLP App source code
COPY . /app

# Install CLP App
RUN pip install --no-cache-dir -e .

ENV PORT=10000
ENV PYTHONUNBUFFERED=1

EXPOSE $PORT

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --preload frappe.app:application"]
