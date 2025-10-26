# Agent-S Dashboard Integration Fix

The dashboard was failing to correctly start and monitor the Agent-S service.

## Problem

The `dashboard.py` configuration for the `agents` service was incorrect:
1.  The `start_cmd` was using a generic python command instead of the dedicated `start-agent-s.sh` script.
2.  The `process_name` was not specific enough, leading to unreliable status checks.
3.  The service `status` was marked as `ready` when it should have been `development` to reflect its current state.

## Solution

The user correctly modified `dashboard.py` to fix the integration:

1.  **`start_cmd`**: Updated to point to the correct script: `f"{PROJECT_DIR}/scripts/start-agent-s.sh"`.
2.  **`process_name`**: Changed to the more specific `"agent_s/server.py"`.
3.  **`status`**: Updated to `"development"`.

After applying these changes and restarting the services, the dashboard now correctly starts, stops, and monitors the Agent-S service. The UI accurately reflects its running state.
