#!/bin/bash
# Stop TTS service (Coqui as fallback)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Stopping Coqui TTS service..."
./tts/stop_coqui_api.sh