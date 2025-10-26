#!/bin/bash
# Start Chatterbox GUI
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎙️ Starting Chatterbox GUI..."

cd "$PROJECT_DIR"
source venv/bin/activate

# Check if already running
if pgrep -f "chatterbox_official_gui.py" > /dev/null; then
    echo "⚠️  Chatterbox GUI already running"
    exit 0
fi

# Start in background
nohup python tts/chatterbox_official_gui.py > logs/chatterbox-gui.log 2>&1 &
PID=$!

echo "✅ Chatterbox GUI started (PID: $PID)"
echo "🌐 Access at: http://localhost:7861"
echo "📋 Logs: logs/chatterbox-gui.log"
