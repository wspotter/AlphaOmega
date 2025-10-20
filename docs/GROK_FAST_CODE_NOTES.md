# Grok Fast Code Briefing

- Launch sequence (Docker off by default): `./scripts/start.sh` then `./scripts/start-dashboard.sh` for the status UI.
- Health checks: `./scripts/check-services.sh` plus `curl http://localhost:8001/health` for Agent-S; MCP OpenAPI at `http://localhost:8002/openapi.json`.
- Docker policy: only ComfyUI and Chatterbox TTS may run in containers. Leave Docker stopped unless starting them via `./scripts/start-comfyui.sh` and `./scripts/start-tts.sh`.
- Text-to-speech: Chatterbox (Docker, port 5003) is the default; legacy Coqui scripts remain for fallback.
- Key logs: `logs/agent_actions.log`, `logs/mcp-unified.log`, `logs/dashboard.log`.
- Hardware/env expectations: AMD MI50 GPUs with `HSA_OVERRIDE_GFX_VERSION=9.0.0`; Agent-S launches through `xvfb-run`.
- Repo state reminder: only the approved Docker services remain; other workloads run locally unless explicitly documented otherwise.
