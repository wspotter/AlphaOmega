#!/usr/bin/env bash
# Start Piper TTS HTTP API with multiple voices
# Requires: piper installed or tts/piper/piper binary, and downloaded voices in tts/

set -euo pipefail
cd "$(dirname "$0")/.."

API_FILE="tts/piper_api.py"
VOICES_DIR="tts"

if [ ! -f "$API_FILE" ]; then
  echo "Missing $API_FILE" >&2
  exit 1
fi

# Download voices if none present
if ! ls "$VOICES_DIR"/*.onnx >/dev/null 2>&1; then
  echo "No Piper voices found. Downloading defaults..."
  bash "$VOICES_DIR"/download_voices.sh || true
fi

# Prefer uvicorn if installed
if command -v uvicorn >/dev/null 2>&1; then
  exec uvicorn tts.piper_api:app --host 0.0.0.0 --port 5002 --log-level info
else
  python3 "$API_FILE"
fi
