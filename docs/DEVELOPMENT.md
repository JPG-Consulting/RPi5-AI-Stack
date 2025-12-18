# Development Guide – Pi AI Stack

This document provides guidance for developers working on the Pi AI Stack codebase.
It explains development workflows, architectural conventions, and dependency policies.

---

## 1. Project Structure

The repository is organized as follows:

```
.
├── backend/
│   ├── ai_api/          # FastAPI backend package
│   ├── requirements.txt # Python dependencies
│   └── .venv/           # Python virtual environment (runtime)
├── web-ui/              # Optional Web UI (static client)
├── docs/                # Project documentation
├── install.sh           # System installer
├── pi-ai-stack.service  # systemd unit
└── config.yaml          # Runtime configuration
```

The backend (`ai_api`) is the **only Python package** and owns all application logic,
policies, and state.

---

## 2. Development Environment

### Python

- Python 3.9+ is required
- Development and production use the same dependency set
- A virtual environment is always used

To create a local venv:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 3. Running the Backend Locally

For local development (without systemd):

```bash
cd backend
. .venv/bin/activate
uvicorn ai_api.main:app --host 127.0.0.1 --port 8000
```

The backend resolves `config.yaml` relative to the package location, not the working
directory, so local execution behaves the same as systemd.

---

## 4. Configuration Handling

- All configuration lives in `config.yaml` at the repository root
- Configuration is loaded once at startup
- The path to `config.yaml` is resolved via `__file__`, not the CWD

This guarantees deterministic behavior across:
- systemd
- local development
- tests

---

## 5. Dependency Versioning Policy

This project targets **ARM64 / Raspberry Pi** environments.

To ensure reliable installation and long-term portability:

- **Avoid strict pins (`==`)** for packages that ship native wheels
  (audio codecs, ML runtimes, ASGI servers).
- **Prefer bounded version ranges**, for example:
  ```
  package>=X.Y,<X+1.0
  ```
- Strict pins (`==`) are acceptable **only** for pure-Python libraries
  and only when required to avoid known regressions.
- Special care must be taken with dependencies distributed via **piwheels**,
  as not all versions are available on ARM.

This policy prevents installation failures caused by missing wheels and avoids
architecture-specific breakage.

---

## 6. Dependency Updates

When updating `backend/requirements.txt`:

1. Prefer widening ranges over narrowing them
2. Test installation on a clean Raspberry Pi OS system
3. Avoid introducing new native dependencies unless strictly required
4. Update documentation if new system packages are needed

---

## 7. systemd and Deployment

- Production execution is handled exclusively by `systemd`
- `install.sh` is the only supported installation method
- There is a single supported service unit: `pi-ai-stack.service`

Local development scripts should not diverge from production behavior.

---

## 8. Testing

- Tests live under `backend/tests/`
- Use `pytest`
- Tests should not depend on external services unless explicitly mocked

Run tests with:

```bash
pytest
```

---

## 9. Web UI Development

The Web UI is a static client:

- No build step required
- No Node.js runtime required at install time
- Communicates exclusively via the OpenAI-compatible API

Backend development must never depend on the Web UI.

---

## 10. Design Principles

- Local-first
- Deterministic startup
- Explicit configuration
- Bounded memory and storage
- Minimal operational complexity

---

End of document.
