# AlphaOmega v2 Migration Plan

## Phase 1: Foundation
- Finalize design system requirements and lay down core style tokens inside `ui/`.
- Define shared runtime contracts inside `core/` (configuration schema, logging, service registry).
- Stub service directories under `services/` with current owners and responsibilities.

## Phase 2: Feature Bridging
- Rebuild the dashboard within the new UI stack using the shared design system.
- Implement the OpenWebUI LLM activity side panel and connect it to telemetry hooks.
- Mirror existing start/stop orchestration scripts inside `scripts/` and align them with the new installer.

## Phase 3: Installer Delivery
- Flesh out `install/setup.sh` into a full bootstrapper (venv creation, dependency install, config templating).
- Write verification scripts to confirm each service comes up (dashboard, Agent-S, ComfyUI, MCPART, TTS, SearxNG).
- Document troubleshooting flows inside `docs/`.

## Phase 4: Cutover and Cleanup
- Validate parity between v1 and v2 service features.
- Announce migration plan, document breaking changes, and sunset redundant files from the repository root.
