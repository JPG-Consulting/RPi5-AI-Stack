# Installation Guide

This guide installs Pi AI Stack on a **Raspberry Pi 5 (8 GB RAM)** running Raspberry Pi OS (64-bit).

## Requirements

- Raspberry Pi 5 (8 GB recommended)
- Raspberry Pi OS (Bookworm, 64-bit)
- Internet connection (for initial install only)

## Quick install

```bash
wget https://example.com/install.sh
chmod +x install.sh
sudo ./install.sh
```

The installer will:
- Update the system
- Install dependencies
- Install Ollama + models
- Install Whisper and Piper
- Create a Python virtualenv
- Install and enable systemd services
- Optionally install the Web UI

The installer is **reboot-safe**: if a reboot is required, it resumes automatically.

## Post-install

- API available at: `http://<pi-ip>/v1`
- Metrics at: `http://<pi-ip>/metrics`
- Web UI at: `http://<pi-ip>/` (if installed)
