#!/usr/bin/env bash
# One-shot deploy script for hi.johnlarckin.com
# Usage on the target server (run as root):
#   bash deploy/deploy.sh
# Or remotely from your laptop:
#   scp -r . root@172.104.141.157:/tmp/johnlarckin && \
#   ssh root@172.104.141.157 'cd /tmp/johnlarckin && bash deploy/deploy.sh'

set -euo pipefail

DOMAIN="hi.johnlarckin.com"
APP_DIR="/srv/johnlarckin"
SERVICE_NAME="johnlarckin"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@johnlarckin.com}"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "Run as root (sudo bash deploy/deploy.sh)" >&2
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx ufw rsync

echo "==> Syncing project to ${APP_DIR}"
mkdir -p "${APP_DIR}"
rsync -a --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude 'deploy/' \
    "${REPO_ROOT}/" "${APP_DIR}/"

echo "==> Creating virtualenv and installing requirements"
python3 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

echo "==> Setting permissions"
chown -R www-data:www-data "${APP_DIR}"

echo "==> Installing systemd unit"
install -m 0644 "${REPO_ROOT}/deploy/johnlarckin.service" "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

echo "==> Configuring nginx"
mkdir -p /var/www/letsencrypt
install -m 0644 "${REPO_ROOT}/deploy/nginx.conf" "/etc/nginx/sites-available/${DOMAIN}.conf"
ln -sf "/etc/nginx/sites-available/${DOMAIN}.conf" "/etc/nginx/sites-enabled/${DOMAIN}.conf"
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> Opening firewall (if ufw enabled)"
if command -v ufw >/dev/null 2>&1; then
    ufw allow OpenSSH || true
    ufw allow 'Nginx Full' || true
fi

echo "==> Requesting Let's Encrypt certificate for ${DOMAIN}"
if host "${DOMAIN}" >/dev/null 2>&1 || getent hosts "${DOMAIN}" >/dev/null 2>&1; then
    certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --email "${ADMIN_EMAIL}" --redirect || \
        echo "WARNING: certbot failed. Check that the A record for ${DOMAIN} points to this server, then run: certbot --nginx -d ${DOMAIN}"
else
    echo "WARNING: ${DOMAIN} does not yet resolve. Add an A record pointing to this server's public IP, then run:"
    echo "    certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email ${ADMIN_EMAIL} --redirect"
fi

echo "==> Done."
echo "Service status:"
systemctl --no-pager --full status "${SERVICE_NAME}.service" | head -20 || true
echo
echo "Visit: http://${DOMAIN}/  (or https:// if certbot succeeded)"
