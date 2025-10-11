#!/bin/bash
# Stop AlphaOmega services

echo "Stopping AlphaOmega services..."

# Stop Docker services
docker-compose down

# Stop Ollama services
pkill -f "ollama serve" || true

# Stop Piper TTS API
pkill -f "piper_api.py" || true

echo "✓ All services stopped"
