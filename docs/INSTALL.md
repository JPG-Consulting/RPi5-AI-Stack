# Installation Guide – Pi AI Stack

This document explains how to install **Pi AI Stack** on a Debian-based system,
such as **Raspberry Pi OS on Raspberry Pi 5**.

The installation is **fully automated** and installs the stack as a **systemd service**.

---

## 1. System Requirements

### Hardware
- Raspberry Pi 5 (8 GB RAM recommended)
- Internet connection (for installation and optional model downloads)

### Software
- Debian-based OS (Raspberry Pi OS recommended)
- Python 3.9+
- systemd
- apt

---

## 2. Installation Overview

The installer will:

- Install required system dependencies
- Deploy the application to `/opt/pi-ai-stack`
- Create a Python virtual environment
- Install Python dependencies
- Install and enable a systemd service
- Start the API automatically

After installation, the API will start automatically on boot.

---

## 3. Installation Steps

### 3.1 Clone the repository

```bash
git clone https://github.com/JPG-Consulting/RPi5-AI-Stack.git
cd RPi5-AI-Stack
```

Ensure that `config.yaml` is present in the repository root before proceeding.

---

### 3.2 Run the installer

```bash
sudo ./install.sh
```

The installer must be run as **root**.

It is safe to re-run the installer; it is **idempotent** and will redeploy the stack.

---

## 4. Installation Layout

After installation, files are deployed to:

```
/opt/pi-ai-stack
├── backend/
│   ├── ai_api/
│   ├── .venv/
│   └── requirements.txt
├── web-ui/
├── data/
├── config.yaml
└── pi-ai-stack.service
```

Key points:

- `config.yaml` remains at the project root
- Runtime data (SQLite, RAG, GC) lives under `data/`
- Python runs inside `backend/.venv`

---

## 5. systemd Service

The installer installs and enables the following service:

```
pi-ai-stack.service
```

### Service behavior

- Starts automatically at boot
- Restarts automatically on failure
- Runs the FastAPI backend via `uvicorn`

### Service management commands

```bash
systemctl status pi-ai-stack
sudo systemctl restart pi-ai-stack
journalctl -u pi-ai-stack -f
```

---

## 6. API Access

By default, the API is available at:

```
http://localhost:8000
```

Example:

```bash
curl http://localhost:8000/v1/models
```

If Nginx is enabled, the API is available via the configured reverse proxy.

---

## 7. Web UI (Optional)

If the Web UI is installed, it is served by Nginx and accessible via:

```
http://<raspberry-ip>/
```

The Web UI is a thin client and uses the same `/v1/*` API as any external client.

---

## 8. Configuration

All configuration is defined in:

```
/opt/pi-ai-stack/config.yaml
```

Changes to the configuration require a service restart:

```bash
sudo systemctl restart pi-ai-stack
```

The backend resolves `config.yaml` independently of the working directory.

---

## 9. Uninstallation

To remove Pi AI Stack:

```bash
sudo systemctl stop pi-ai-stack
sudo systemctl disable pi-ai-stack
sudo rm -f /etc/systemd/system/pi-ai-stack.service
sudo rm -rf /opt/pi-ai-stack
sudo systemctl daemon-reload
```

---

## 10. Troubleshooting

### Service fails to start

```bash
journalctl -u pi-ai-stack -n 50 --no-pager
```

Common causes:
- Missing or invalid `config.yaml`
- Python dependency installation failure
- Port already in use

---

## 11. Notes

- The installer does not modify system firewall rules
- No external databases are required
- The stack is designed to run entirely locally

---

End of document.
