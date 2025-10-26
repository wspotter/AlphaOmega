#!/bin/bash

set -e

echo "🚀 Installing Embedding-based Intent Detection"
echo ""

# Make setup script executable
chmod +x scripts/setup-embedding-model.sh

# Run setup
./scripts/setup-embedding-model.sh

# Copy updated pipeline
echo ""
echo "📋 Updating pipeline..."
cp pipelines/alphaomega_router.py openwebui_data/pipelines/alphaomega_router.py

# Restart OpenWebUI
echo ""
echo "🔄 Restarting OpenWebUI..."
pkill -f "open-webui" 2>/dev/null || true
sleep 2

cd /home/stacy/AlphaOmega
source venv/bin/activate
open-webui serve --host 0.0.0.0 --port 8080 > logs/openwebui.log 2>&1 &

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Wait 10 seconds for OpenWebUI to start"
echo "2. Open http://localhost:8080"
echo "3. Select 'AlphaOmega' model"
echo "4. Test: 'schedule a meeting with the team'"
echo ""
echo "To test accuracy improvements:"
echo "  python test_embedding_intent.py"