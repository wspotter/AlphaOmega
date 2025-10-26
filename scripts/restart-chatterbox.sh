#!/bin/bash
# Restart Chatterbox TTS with new emotion support

echo "🎤 Restarting Chatterbox TTS..."

# Stop current instance
echo "Stopping current Chatterbox instance..."
sudo pkill -f chatterbox_api
sleep 2

# Verify it stopped
if pgrep -f chatterbox_api > /dev/null; then
    echo "⚠️  Force killing Chatterbox..."
    sudo pkill -9 -f chatterbox_api
    sleep 1
fi

# Start new instance
echo "Starting Chatterbox with emotion support..."
cd /home/stacy/AlphaOmega
source venv/bin/activate

# Run in background
nohup python tts/chatterbox_api.py > logs/chatterbox.log 2>&1 &
CHATTERBOX_PID=$!

echo "Chatterbox starting (PID: $CHATTERBOX_PID)..."
sleep 5

# Check if it's running
if curl -s http://localhost:5003/health > /dev/null 2>&1; then
    echo "✅ Chatterbox is running!"
    echo ""
    echo "Test emotions endpoint:"
    echo "  curl http://localhost:5003/v1/emotions | jq '.'"
    echo ""
    echo "Test happy emotion:"
    echo "  curl -X POST http://localhost:5003/v1/audio/speech \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"input\": \"Hello!\", \"emotion\": \"happy\"}' \\"
    echo "    --output test.wav"
else
    echo "❌ Chatterbox failed to start!"
    echo "Check logs: tail -f logs/chatterbox.log"
    exit 1
fi
