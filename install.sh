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

OLLAMA_API="http://127.0.0.1:11434"
OLLAMA_MODELS=(
  "llama3.2:3b"
  "llama3.2:1b"
  "nomic-embed-text"
)

echo "==> Installing Pi AI Stack"

# ------------------------------------------------------------
# 1. Preconditions
# ------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This installer must be run as root (use sudo)."
  exit 1
fi

for cmd in python3 systemctl apt-get curl; do
  command -v "$cmd" >/dev/null || {
    echo "ERROR: Required command not found: $cmd"
    exit 1
  }
done

# ------------------------------------------------------------
# 2. Stop existing services (if any)
# ------------------------------------------------------------

systemctl stop "${SERVICE_NAME}" 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

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
# 4. Install Ollama (mandatory)
# ------------------------------------------------------------

if ! command -v ollama >/dev/null; then
  echo "==> Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "==> Ollama already installed"
fi

echo "==> Enabling and starting Ollama"
systemctl enable ollama
systemctl start ollama

echo "==> Waiting for Ollama API to be available"
until curl -s "${OLLAMA_API}/api/tags" >/dev/null; do
  sleep 1
done

# ------------------------------------------------------------
# 5. Pull required Ollama models
# ------------------------------------------------------------

echo "==> Ensuring required Ollama models are available"

for model in "${OLLAMA_MODELS[@]}"; do
  if ollama list | grep -q "^${model}\b"; then
    echo "  - Model already present: ${model}"
  else
    echo "  - Pulling model: ${model}"
    ollama pull "${model}"
  fi
done

# ------------------------------------------------------------
# 6. Deploy application
# ------------------------------------------------------------

echo "==> Deploying application to ${INSTALL_DIR}"
rm -rf "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
cp -r . "${INSTALL_DIR}"

# ------------------------------------------------------------
# 7. Validate required files
# ------------------------------------------------------------

[[ -f "${INSTALL_DIR}/config.yaml" ]] || { echo "ERROR: config.yaml missing"; exit 1; }
[[ -f "${INSTALL_DIR}/backend/requirements.txt" ]] || { echo "ERROR: backend/requirements.txt missing"; exit 1; }
[[ -f "${INSTALL_DIR}/pi-ai-stack.service" ]] || { echo "ERROR: pi-ai-stack.service missing"; exit 1; }

# ------------------------------------------------------------
# 8. Runtime directories
# ------------------------------------------------------------

mkdir -p "${INSTALL_DIR}/data"

# ------------------------------------------------------------
# 9. Python virtual environment
# ------------------------------------------------------------

echo "==> Setting up Python virtual environment"
VENV_DIR="${INSTALL_DIR}/backend/.venv"
python3 -m venv "${VENV_DIR}"

"${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/backend/requirements.txt"

# ------------------------------------------------------------
# 10. Install systemd service (backend)
# ------------------------------------------------------------

echo "==> Installing backend systemd service"
cp "${INSTALL_DIR}/pi-ai-stack.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# ------------------------------------------------------------
# 11. Configure Nginx (mandatory)
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
# 12. Start services
# ------------------------------------------------------------

echo "==> Starting services"
systemctl restart nginx
systemctl restart "${SERVICE_NAME}"

sleep 2

systemctl is-active --quiet ollama || {
  echo "ERROR: Ollama failed to start"
  journalctl -u ollama -n 50 --no-pager
  exit 1
}

systemctl is-active --quiet nginx || {
  echo "ERROR: Nginx failed to start"
  journalctl -u nginx -n 50 --no-pager
  exit 1
}

systemctl is-active --quiet "${SERVICE_NAME}" || {
  echo "ERROR: Pi AI Stack backend failed to start"
  journalctl -u "${SERVICE_NAME}" -n 50 --no-pager
  exit 1
}

# ------------------------------------------------------------
# 13. Final output
# ------------------------------------------------------------

echo
echo "Pi AI Stack installed successfully."
echo
echo "Web UI:  http://<raspberry-ip>/"
echo "API:     http://<raspberry-ip>/v1/"
echo
echo "Logs:"
echo "  Backend: journalctl -u ${SERVICE_NAME} -f"
echo "  Ollama:  journalctl -u ollama -f"
echo "  Nginx:   journalctl -u nginx -f"
echo
