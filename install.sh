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

PIPER_MODEL_DIR="${INSTALL_DIR}/models"
PIPER_MODEL_BASENAME="es_ES-carlfm-low"
PIPER_MODEL_PATH="${PIPER_MODEL_DIR}/${PIPER_MODEL_BASENAME}.onnx"
PIPER_MODEL_CONFIG_PATH="${PIPER_MODEL_DIR}/${PIPER_MODEL_BASENAME}.onnx.json"
PIPER_MODEL_URLS=(
  "https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/${PIPER_MODEL_BASENAME}.onnx"
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/low/${PIPER_MODEL_BASENAME}.onnx"
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/low/${PIPER_MODEL_BASENAME}.onnx"
)
PIPER_MODEL_CONFIG_URLS=(
  "https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/${PIPER_MODEL_BASENAME}.onnx.json"
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/low/${PIPER_MODEL_BASENAME}.onnx.json"
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/carlfm/low/${PIPER_MODEL_BASENAME}.onnx.json"
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

ollama_is_installed() {
  command -v ollama >/dev/null 2>&1 || return 1
  [[ -f /etc/systemd/system/ollama.service ]] || return 1
  return 0
}

install_ollama() {
  local max_attempts=5
  local attempt=1

  while (( attempt <= max_attempts )); do
    echo "==> Installing Ollama (attempt $attempt/$max_attempts)"

    # Cleanup partial installs
    systemctl stop ollama 2>/dev/null || true
    rm -f /usr/local/bin/ollama
    rm -rf /usr/local/lib/ollama
    rm -rf /var/lib/ollama

    if curl -fsSL https://ollama.com/install.sh | sh; then
      if ollama_is_installed; then
        echo "==> Ollama installed successfully"
        return 0
      fi
    fi

    echo "!! Ollama install attempt $attempt failed"
    attempt=$((attempt + 1))
    sleep $((attempt * 3))
  done

  echo "ERROR: Ollama could not be installed after $max_attempts attempts"
  return 1
}

wait_for_ollama_api() {
  local timeout=120
  local waited=0

  echo "==> Waiting for Ollama API to become available"

  until curl -fsS --max-time 2 "${OLLAMA_API}/api/tags" >/dev/null 2>&1; do
    sleep 2
    waited=$((waited + 2))

    if (( waited >= timeout )); then
      echo "ERROR: Ollama API did not become available after ${timeout}s"
      journalctl -u ollama -n 50 --no-pager || true
      return 1
    fi
  done

  echo "==> Ollama API is available"
  return 0
}

download_with_retries() {
  local url="$1"
  local dest="$2"
  local max_attempts=5
  local attempt=1

  while (( attempt <= max_attempts )); do
    echo "==> Downloading ${url} (attempt ${attempt}/${max_attempts})"
    if curl -fL --retry 3 --retry-delay 2 -o "${dest}" "${url}"; then
      return 0
    fi

    echo "!! Download failed for ${url}"
    attempt=$((attempt + 1))
    sleep $((attempt * 2))
  done

  echo "ERROR: Unable to download ${url} after ${max_attempts} attempts"
  return 1
}

ensure_piper_asset() {
  local url="$1"
  local dest="$2"

  if [[ -s "${dest}" ]]; then
    echo "  - Piper asset already present: ${dest}"
    return 0
  fi

  mkdir -p "$(dirname "${dest}")"
  local tmp
  tmp="$(mktemp)"
  if download_with_retries "${url}" "${tmp}"; then
    mv "${tmp}" "${dest}"
    return 0
  fi

  rm -f "${tmp}"
  return 1
}

ensure_piper_asset_with_fallback() {
  local urls_name="$1"
  local dest="$2"
  local -n urls_ref="${urls_name}"

  if [[ -s "${dest}" ]]; then
    echo "  - Piper asset already present: ${dest}"
    return 0
  fi

  mkdir -p "$(dirname "${dest}")"
  local tmp
  tmp="$(mktemp)"
  for url in "${urls_ref[@]}"; do
    echo "==> Attempting Piper asset download from ${url}"
    if download_with_retries "${url}" "${tmp}"; then
      mv "${tmp}" "${dest}"
      return 0
    fi
  done

  rm -f "${tmp}"
  echo "ERROR: Unable to download Piper asset to ${dest}"
  return 1
}

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
# 2. Stop existing services
# ------------------------------------------------------------

systemctl stop "${SERVICE_NAME}" 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
systemctl stop ollama 2>/dev/null || true

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
# 4. Ollama installation & startup (definitive)
# ------------------------------------------------------------

if ollama_is_installed; then
  echo "==> Ollama already installed"
else
  install_ollama || exit 1
fi

echo "==> Enabling and starting Ollama"
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

wait_for_ollama_api || exit 1

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
# 8. Runtime directories & Piper model
# ------------------------------------------------------------

mkdir -p "${INSTALL_DIR}/data"
mkdir -p "${PIPER_MODEL_DIR}"

echo "==> Ensuring Piper TTS model assets"
ensure_piper_asset_with_fallback PIPER_MODEL_URLS "${PIPER_MODEL_PATH}"
ensure_piper_asset_with_fallback PIPER_MODEL_CONFIG_URLS "${PIPER_MODEL_CONFIG_PATH}"

# ------------------------------------------------------------
# 9. Python virtual environment
# ------------------------------------------------------------

echo "==> Setting up Python virtual environment"
VENV_DIR="${INSTALL_DIR}/backend/.venv"
python3 -m venv "${VENV_DIR}"

"${VENV_DIR}/bin/pip" install --upgrade pip wheel setuptools
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/backend/requirements.txt"

# ------------------------------------------------------------
# 10. Install backend systemd service
# ------------------------------------------------------------

echo "==> Installing backend systemd service"
cp "${INSTALL_DIR}/pi-ai-stack.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# ------------------------------------------------------------
# 11. Configure Nginx
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
