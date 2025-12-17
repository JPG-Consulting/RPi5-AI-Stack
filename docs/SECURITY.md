# Security

## Threat model

- Trusted LAN
- Single-user by default

## Measures

- Nginx hardening
- `/internal/*` endpoints restricted to localhost
- No secrets in environment variables
- No persistence of raw audio

TLS and authentication can be added externally if required.
