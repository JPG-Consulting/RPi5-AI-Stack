#!/usr/bin/env bash
# Pi AI Stack installer
# Target: Debian-based systems (Raspberry Pi OS recommended)
# Install path: /opt/pi-ai-stack

set -euo pipefail
IFS=$'\n\t'

INSTALL_DIR="/opt/pi-ai-stack"
SERVICE_NAME="pi-ai-stack"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
NGINX_SITE="pi-ai-stack"
NGINX_AVAILABLE="/etc/nginx/sites-available/${NGINX_SITE}"
NGINX_ENABLED="/etc/nginx/sites-enabled/${NGINX_SITE}"

echo "==> Installing Pi AI Stack"

# ------------------------------------------------------------
# 1. Preconditions
# ------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This installer must be run as root (use sudo)."
  exit 1
fi

for cmd in python3 systemctl apt-get; do
  command -v "$cmd" >/dev/null || {
    echo "ERROR: Required command not found: $cmd"
    exit 1
  }
done

# ------------------------------------------------------------
# 2. Stop existing services (if any)
# ------------------------------------------------------------

if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
  echo "==> Stopping existing Pi AI Stack service"
  systemctl stop "${SERVICE_NAME}" || true
fi

if systemctl list-unit-files | grep -q "^nginx.service"; then
  echo "==> Stopping existing Nginx service"
  systemctl stop nginx || true
fi

# ------------------------------------------------------------
# 3. System dependencies (INCLUDING NGINX)
# ------------------------------------------------------------

echo "==> Installing system dependencies"
apt-get update
apt-get install -y \
  python3-venv \
  python3-dev \
  python3-pip \
  build-essential \
  pkg-config \
  libffi-dev \
  libssl-dev \
  ffmpeg \
  curl \
  ca-certificates \
  nginx

# ------------------------------------------------------------
# 4. Deploy application
# ------------------------------------------------------------

echo "==> Deploying application to ${INSTALL_DIR}"

rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
cp -r . "${INSTALL_DIR}"

# ------------------------------------------------------------
# 5. Validate required files
# ------------------------------------------------------------

if [[ ! -f "${INSTALL_DIR}/config.yaml" ]]; then
  echo "ERROR: config.yaml not found in ${INSTALL_DIR}"
  exit 1
fi

if [[ ! -f "${INSTALL_DIR}/backend/ai_api/main.py" ]]; then
  echo "ERROR: backend/ai_api/main.py not found"
  exit 1
fi

if [[ ! -f "${INSTALL_DIR}/pi-ai-stack.service" ]]; then
  echo "ERROR: pi-ai-stack.service not found"
  exit 1
fi

# ------------------------------------------------------------
# 6. Runtime directories
# ------------------------------------------------------------

echo "==> Creating runtime directories"
mkdir -p "${INSTALL_DIR}/data"

# ------------------------------------------------------------
# 7. Python virtual environment
# ------------------------------------------------------------

echo "==> Setting up Python virtual environment"

VENV_DIR="${INSTALL_DIR}/backend/.venv"
python3 -m venv "${VENV_DIR}"

"${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools

REQ_FILE="${INSTALL_DIR}/backend/requirements.txt"
if [[ ! -f "${REQ_FILE}" ]]; then
  echo "ERROR: backend/requirements.txt not found"
  exit 1
fi

"${VENV_DIR}/bin/pip" install -r "${REQ_FILE}"

# ------------------------------------------------------------
# 8. Install systemd service
# ------------------------------------------------------------

echo "==> Installing Pi AI Stack systemd service"

cp "${INSTALL_DIR}/pi-ai-stack.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# ------------------------------------------------------------
# 9. Configure Nginx
# ------------------------------------------------------------

echo "==> Configuring Nginx"

cat > "${NGINX_AVAILABLE}" <<'EOF'
server {
    listen 80;
    server_name _;

    root /opt/pi-ai-stack/web-ui;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /v1/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf "${NGINX_AVAILABLE}" "${NGINX_ENABLED}"

nginx -t
systemctl enable nginx

# ------------------------------------------------------------
# 10. Start services
# ------------------------------------------------------------

echo "==> Starting services"

systemctl restart nginx
systemctl restart "${SERVICE_NAME}"

sleep 2

if ! systemctl is-active --quiet nginx; then
  echo "ERROR: Nginx failed to start"
  journalctl -u nginx -n 50 --no-pager
  exit 1
fi

if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
  echo "ERROR: Pi AI Stack service failed to start"
  journalctl -u "${SERVICE_NAME}" -n 50 --no-pager
  exit 1
fi

# ------------------------------------------------------------
# 11. Final output
# ------------------------------------------------------------

echo
echo "Pi AI Stack installed successfully."
echo
echo "Web UI:  http://<raspberry-ip>/"
echo "API:     http://<raspberry-ip>/v1/"
echo
echo "Logs:"
echo "  Backend: journalctl -u ${SERVICE_NAME} -f"
echo "  Nginx:   journalctl -u nginx -f"
echo
