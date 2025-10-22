#!/bin/bash
# Start ComfyUI image generation service (LOCAL, AMD ROCm)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMFYUI_DIR="${COMFYUI_DIR:-/opt/ComfyUI}"
PORT="${COMFYUI_PORT:-8188}"
GPU_INDEX="${COMFYUI_GPU:-2}"
HSA_VERSION="${HSA_OVERRIDE_GFX_VERSION:-9.0.0}"
PID_FILE="/tmp/comfyui.pid"
LOG_FILE="${PROJECT_ROOT}/logs/comfyui.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "ComfyUI already running (PID: $OLD_PID) on port ${PORT}."
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Create symlinks to AlphaOmega directories
mkdir -p "${PROJECT_ROOT}/models/comfyui"
mkdir -p "${PROJECT_ROOT}/comfyui_bridge/workflows"
mkdir -p "${PROJECT_ROOT}/comfyui_bridge/output"
mkdir -p "${PROJECT_ROOT}/logs"

# Link models and outputs
sudo rm -rf "${COMFYUI_DIR}/models" 2>/dev/null || true
sudo ln -sf "${PROJECT_ROOT}/models/comfyui" "${COMFYUI_DIR}/models"
sudo rm -rf "${COMFYUI_DIR}/output" 2>/dev/null || true
sudo ln -sf "${PROJECT_ROOT}/comfyui_bridge/output" "${COMFYUI_DIR}/output"

echo "Starting ComfyUI on port ${PORT} (GPU ${GPU_INDEX})..."

# Start ComfyUI with ROCm environment
cd "${COMFYUI_DIR}"
HSA_OVERRIDE_GFX_VERSION="${HSA_VERSION}" \
ROCR_VISIBLE_DEVICES="${GPU_INDEX}" \
nohup sudo -E venv/bin/python main.py --listen --port "${PORT}" > "${LOG_FILE}" 2>&1 &

COMFYUI_PID=$!
echo "$COMFYUI_PID" > "$PID_FILE"

# Wait for startup
sleep 3

if ps -p "$COMFYUI_PID" > /dev/null 2>&1; then
    echo "✓ ComfyUI started successfully!"
    echo "   PID: $COMFYUI_PID"
    echo "   URL: http://localhost:${PORT}"
    echo "   Logs: ${LOG_FILE}"
else
    echo "✗ Failed to start ComfyUI. Check logs: ${LOG_FILE}"
    rm -f "$PID_FILE"
    exit 1
fi
