#!/usr/bin/env bash
# Pi AI Stack installer
# Target: Debian-based systems (Raspberry Pi OS recommended)
# Install path: /opt/pi-ai-stack

set -euo pipefail
IFS=$'\n\t'

INSTALL_DIR="/opt/pi-ai-stack"
SERVICE_NAME="pi-ai-stack"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

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
# 2. Stop existing service (if any)
# ------------------------------------------------------------

if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
  echo "==> Stopping existing service"
  systemctl stop "${SERVICE_NAME}" || true
fi

# ------------------------------------------------------------
# 3. System dependencies
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
  ca-certificates

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

echo "==> Installing systemd service"

cp "${INSTALL_DIR}/pi-ai-stack.service" "${SERVICE_FILE}"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# ------------------------------------------------------------
# 9. Start and verify service
# ------------------------------------------------------------

echo "==> Starting service"
systemctl restart "${SERVICE_NAME}"

sleep 2

if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
  echo "ERROR: Service failed to start"
  echo "---- Last logs ----"
  journalctl -u "${SERVICE_NAME}" -n 50 --no-pager
  exit 1
fi

# ------------------------------------------------------------
# 10. Final output
# ------------------------------------------------------------

echo
echo "Pi AI Stack installed successfully."
echo "API available at: http://localhost:8000"
echo "View logs with: journalctl -u ${SERVICE_NAME} -f"
echo
