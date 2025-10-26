# AlphaOmega v2

The v2 workspace rebuilds AlphaOmega around a cleaner module layout, consistent UI design, and a turnkey installation flow.

## Objectives
- Unify dashboards, OpenWebUI custom extensions, and MCP tooling under a shared visual system.
- Add a live LLM activity side panel to the OpenWebUI chat surface.
- Ship an all-in-one installer that provisions every local service with minimal steps.

## Directory Layout
- `core/` – foundational runtime pieces shared across services (configuration, orchestration helpers, shared libs).
- `services/` – long-running backends (Agent-S, ComfyUI bridge, TTS, etc.).
- `ui/` – user-facing surfaces (web dashboard, OpenWebUI customizations, MCPART GUI polish).
- `install/` – installer assets and provisioning scripts.
- `scripts/` – operational utilities (start/stop/supervisor wrappers, health checks).
- `docs/` – v2-specific documentation, diagrams, and decision records.
- `packages/` – reusable Python or Node packages published from AlphaOmega.

## Next Steps
1. Build a shared design kit inside `ui/` (palette, typography, component tokens).
2. Prototype the OpenWebUI side frame for real-time LLM telemetry.
3. Port each service from v1 into the new layout, adding install hooks along the way.
4. Automate environment setup inside `install/` and document the process in `docs/`.
