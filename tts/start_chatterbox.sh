#!/bin/bash
# Build and run Chatterbox TTS in Docker

cd "$(dirname "$0")/.."

echo "Building Chatterbox TTS Docker image..."
docker build -f tts/Dockerfile.chatterbox -t alphaomega-chatterbox:latest tts/

echo ""
echo "Starting Chatterbox TTS service..."
docker run -d \
  --name alphaomega-chatterbox \
  --gpus all \
  -p 5003:5003 \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  alphaomega-chatterbox:latest

echo ""
echo "✓ Chatterbox TTS started on port 5003"
echo "✓ API endpoint: http://localhost:5003/v1/audio/speech"
echo ""
echo "Test with:"
echo "  curl -X POST http://localhost:5003/v1/audio/speech \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"model\":\"tts-1\",\"input\":\"Hello from Chatterbox!\",\"voice\":\"alloy\"}' \\"
echo "    --output test_chatterbox.wav"
