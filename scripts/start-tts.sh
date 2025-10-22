#!/bin/bash
# Start TTS service (Coqui as fallback)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Coqui TTS service (fallback)..."
./tts/start_coqui_api.sh