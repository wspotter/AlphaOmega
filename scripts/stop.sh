#!/bin/bash
# Stop AlphaOmega services

echo "Stopping AlphaOmega services..."

# Stop Docker services
docker-compose down

# Stop Ollama services
pkill -f "ollama serve" || true

echo "✓ All services stopped"
