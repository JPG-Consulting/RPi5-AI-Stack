# INSTALL – Pi AI Stack

This document explains how to install the **Pi AI Stack** on a Raspberry Pi 5.

The installation is designed to be:

* reproducible
* reboot-safe
* idempotent
* suitable for unattended installs

---

## 1. Requirements

### Hardware

* Raspberry Pi 5
* 8 GB RAM (required)
* Active cooling strongly recommended
* microSD or NVMe storage (NVMe recommended)

### Software

* Raspberry Pi OS 64-bit (Bookworm)
* Fresh system recommended
* Internet access during installation

---

## 2. Quick Install

The entire stack can be installed with a single command:

```bash
curl -fsSL https://<repo-url>/install.sh | sudo bash
```

This command:

* updates the system
* installs all dependencies
* installs and configures the AI stack
* enables and starts required services

---

## 3. What the Installer Does

The installer performs the following steps:

1. System update (`apt update && apt upgrade`)
2. Installs system dependencies
3. Installs Ollama
4. Downloads the configured LLM model
5. Installs Whisper (STT)
6. Installs Piper (TTS)
7. Creates a Python virtual environment
8. Installs backend dependencies
9. Installs and configures Nginx
10. Registers systemd services

The installer is **idempotent**:

* it can be safely re-run
* interrupted installs resume automatically after reboot

---

## 4. Reboot Handling

Some steps (kernel, firmware, GPU drivers) may require a reboot.

If a reboot is required:

* the installer records its current stage
* the system reboots automatically
* installation resumes from the last completed step

No manual intervention is required.

---

## 5. Installed Components

### Ollama (LLM Runtime)

* Installed system-wide
* Runs as a system service
* Configured via `config.yaml`
* Not exposed directly to the network

### Backend API (FastAPI)

* Runs in a Python virtual environment
* Exposes an OpenAI-compatible API
* Bound to `127.0.0.1`
* Managed by systemd

### Nginx

* Acts as the single entry point
* Exposes the API to the local network
* Streaming-safe (buffering disabled)

### Speech Components

* **Whisper** for Speech-to-Text (batch)
* **Piper** for Text-to-Speech (streaming)

Audio is never persisted.

---

## 6. Directory Layout

The stack is installed under:

```
/opt/pi-ai-stack/
```

Typical layout:

```
/opt/pi-ai-stack/
├── backend/
├── frontend/        # optional Web UI
├── venv/
├── config.yaml
├── data/
│   ├── conversations.db
│   └── rag/
└── logs/
```

Permissions:

* owned by `root:root`
* services run with least privileges

---

## 7. Configuration

After installation, edit:

```
/opt/pi-ai-stack/config.yaml
```

Common adjustments:

* change Ollama model
* adjust conversation TTL
* tune context limits
* enable OpenAI fallback

Restart services after configuration changes:

```bash
sudo systemctl restart pi-ai-api
```

---

## 8. Optional Web UI

The Web UI provides a ChatGPT-like interface.

To enable it during installation:

```bash
INSTALL_WEB_UI=true curl -fsSL https://<repo-url>/install.sh | sudo bash
```

Characteristics:

* runs locally
* consumes the same API
* supports streaming chat and audio

---

## 9. Backup & Restore (Basic)

To back up all user data:

```bash
sudo systemctl stop pi-ai-api
sudo tar czf pi-ai-backup.tar.gz /opt/pi-ai-stack/data
sudo systemctl start pi-ai-api
```

To restore:

```bash
sudo systemctl stop pi-ai-api
sudo tar xzf pi-ai-backup.tar.gz -C /
sudo systemctl start pi-ai-api
```

---

## 10. Uninstallation

To remove the stack:

```bash
sudo systemctl stop pi-ai-api
sudo systemctl stop ollama
sudo rm -rf /opt/pi-ai-stack
```

System packages installed as dependencies are not removed automatically.

---

## 11. Notes & Recommendations

* Monitor CPU temperature on Raspberry Pi 5
* Prefer OPUS or PCM for low-latency TTS
* Keep conversation TTL reasonable to avoid disk growth
* Do not expose the API to the public internet without TLS and authentication

---

## 12. Summary

The Pi AI Stack installer provides:

* a one-command installation
* automatic recovery after reboot
* a fully local AI assistant
* a clean and inspectable deployment

Once installed, the system is ready for immediate use.
