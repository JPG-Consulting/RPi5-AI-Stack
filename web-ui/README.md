# Pi AI Stack Web UI

Static Web UI (no build step). Served by Nginx from `/opt/pi-ai-stack/web-ui`.

- Chat streaming: `/v1/chat/completions` (POST + SSE)
- TTS streaming: `/v1/audio/speech` (`opus`)

Open:
http://<pi-ip>/
