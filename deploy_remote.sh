#!/bin/bash
# ==============================================================================
# Customer Loyalty Program (CLP) - 1-Click Production Cloud Server Deployer
# Target OS: Ubuntu 22.04 LTS (64-bit)
# Stack: Python 3.10, Node.js 18, MariaDB 10.6, Redis, Nginx, Supervisor, Frappe v14
# ==============================================================================

set -e

DOMAIN_NAME="${1:-clp.rsrtechnologies.co.in}"
ADMIN_PASSWORD="${2:-Admin@12345}"

echo "=================================================================="
echo " Starting Automated CLP Production Deployment"
echo " Domain: $DOMAIN_NAME"
echo " Date: $(date)"
echo "=================================================================="

# 1. Update system & install dependencies
echo ">>> [1/6] Installing System Packages..."
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y
apt install -y git python3-dev python3-pip python3-venv python3-setuptools \
    redis-server mariadb-server mariadb-client xvfb libfontconfig wkhtmltopdf \
    curl build-essential supervisor nginx certbot python3-certbot-nginx

# 2. Install Node.js 18 and Yarn
echo ">>> [2/6] Installing Node.js 18 and Yarn..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi
npm install -g yarn

# 3. Configure MariaDB for Frappe
echo ">>> [3/6] Configuring MariaDB..."
tee /etc/mysql/mariadb.conf.d/frappe.cnf > /dev/null << 'EOF'
[mysqld]
innodb-file-format=barracuda
innodb-file-per-table=1
innodb-large-prefix=1
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF

systemctl restart mariadb
systemctl enable mariadb
systemctl enable redis-server

# 4. Create frappe system user
echo ">>> [4/6] Creating Frappe User & Initializing Bench..."
id -u frappe &>/dev/null || adduser --disabled-password --gecos "" frappe
usermod -aG sudo frappe
echo "frappe ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/frappe

# 5. Bench & App Installation as frappe user
su - frappe -c "
set -e
pip3 install frappe-bench

if [ ! -d '/home/frappe/frappe-bench' ]; then
    echo 'Initializing Frappe Bench version-14...'
    bench init --frappe-branch version-14 frappe-bench
fi

cd /home/frappe/frappe-bench

if [ ! -d 'apps/clp' ]; then
    echo 'Fetching CLP Application from GitHub...'
    bench get-app https://github.com/Anilbirada/CLP-Application.git
fi

if [ ! -d 'sites/$DOMAIN_NAME' ]; then
    echo 'Creating new site $DOMAIN_NAME...'
    bench new-site $DOMAIN_NAME --admin-password '$ADMIN_PASSWORD'
    bench --site $DOMAIN_NAME install-app clp
fi
"

# 6. Setup Production (Supervisor + Nginx)
echo ">>> [5/6] Setting Up 24/7 Supervisor and Nginx..."
su - frappe -c "
cd /home/frappe/frappe-bench
sudo bench setup production frappe --yes
bench setup nginx
sudo systemctl reload nginx
sudo supervisorctl reload
"

echo "=================================================================="
echo " ✅ CLP Production Deployment Completed!"
echo " Site: http://$DOMAIN_NAME"
echo " Note: To enable SSL, run: sudo certbot --nginx -d $DOMAIN_NAME"
echo "=================================================================="
