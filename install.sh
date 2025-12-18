#!/usr/bin/env bash
set -euo pipefail

### CONFIG ###
INSTALL_DIR="/opt/pi-ai-stack"
STATE_FILE="$INSTALL_DIR/install.state"
PYTHON_VERSION="3.11"
OLLAMA_MODEL_MAIN="llama3.2:3b"
OLLAMA_MODEL_FACTS="llama3.2:1b"
OLLAMA_MODEL_EMBED="nomic-embed-text"

### HELPERS ###
log() {
  echo "[install] $1"
}

require_root() {
  if [[ "$EUID" -ne 0 ]]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
  fi
}

save_state() {
  echo "$1" > "$STATE_FILE"
}

load_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cat "$STATE_FILE"
  else
    echo "start"
  fi
}

### STEPS ###
step_system_update() {
  log "Updating system"
  apt-get update
  apt-get upgrade -y
}

step_install_packages() {
  log "Installing system packages"
  apt-get install -y \
    python3 python3-venv python3-pip \
    git curl wget \
    ffmpeg \
    nginx \
    sqlite3
}

step_install_ollama() {
  if ! command -v ollama >/dev/null; then
    log "Installing Ollama"
    curl -fsSL https://ollama.com/install.sh | sh
  else
    log "Ollama already installed"
  fi

  systemctl enable ollama
  systemctl start ollama

  log "Pulling Ollama models"
  ollama pull "$OLLAMA_MODEL_MAIN"
  ollama pull "$OLLAMA_MODEL_FACTS"
  ollama pull "$OLLAMA_MODEL_EMBED"
}

step_prepare_dirs() {
  log "Creating directories"
  mkdir -p "$INSTALL_DIR"/{backend,data,logs}
}

step_copy_repo() {
  log "Copying repository files"
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.github' \
    ./ "$INSTALL_DIR/"
}

step_python_env() {
  log "Setting up Python virtualenv"
  cd "$INSTALL_DIR/backend"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
}

step_nginx() {
  log "Configuring Nginx"
  cp nginx.pi-ai-stack.conf /etc/nginx/sites-available/pi-ai-stack
  ln -sf /etc/nginx/sites-available/pi-ai-stack /etc/nginx/sites-enabled/pi-ai-stack
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl reload nginx
}

step_systemd() {
  log "Installing systemd service"
  cp pi-ai-stack.service /etc/systemd/system/pi-ai-stack.service
  systemctl daemon-reload
  systemctl enable pi-ai-stack
  systemctl restart pi-ai-stack
}

step_reboot_if_needed() {
  if [[ -f /var/run/reboot-required ]]; then
    log "Reboot required, resuming after reboot"
    save_state "post-reboot"
    reboot
  fi
}

### MAIN ###
require_root
STATE="$(load_state)"

case "$STATE" in
  start)
    step_system_update
    save_state "packages"
    step_reboot_if_needed
    ;;
  packages)
    step_install_packages
    save_state "ollama"
    ;;
  ollama)
    step_install_ollama
    save_state "dirs"
    ;;
  dirs)
    step_prepare_dirs
    save_state "copy"
    ;;
  copy)
    step_copy_repo
    save_state "python"
    ;;
  python)
    step_python_env
    save_state "nginx"
    ;;
  nginx)
    step_nginx
    save_state "systemd"
    ;;
  systemd)
    step_systemd
    save_state "done"
    ;;
  post-reboot)
    log "Resuming after reboot"
    save_state "packages"
    ;;
  done)
    log "Installation already completed"
    ;;
  *)
    echo "Unknown install state: $STATE"
    exit 1
    ;;
esac

log "Installation step '$STATE' completed"
