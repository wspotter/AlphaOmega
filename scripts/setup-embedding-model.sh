#!/bin/bash

echo "🧠 Setting up embedding-based intent detection..."
echo ""

# Recommended embedding models
MODELS=(
    "qwen3:8b-instruct-q4_K_M"  # Best accuracy (RECOMMENDED)
    "bge-small-en-v1.5"         # Fastest, lower VRAM (~0.5GB)
    "nomic-embed-text"          # Good balance, small
)

echo "Available embedding models:"
echo "1. qwen3:8b-instruct-q4_K_M  - Best accuracy (~5-6GB VRAM)"
echo "2. bge-small-en-v1.5        - Fastest, low VRAM (~0.5GB)"
echo "3. nomic-embed-text         - Good balance (~0.3GB)"
echo ""

read -p "Which model to pull? (1-3, or 'all' for testing): " choice

case $choice in
    1)
        echo "Pulling qwen3:8b-instruct-q4_K_M (best accuracy)..."
        ollama pull qwen3:8b-instruct-q4_K_M
        echo "export EMBEDDING_MODEL=qwen3:8b-instruct-q4_K_M" >> .env
        ;;
    2)
        echo "Pulling bge-small-en-v1.5 (fastest)..."
        ollama pull bge-small-en-v1.5
        echo "export EMBEDDING_MODEL=bge-small-en-v1.5" >> .env
        ;;
    3)
        echo "Pulling nomic-embed-text (balanced)..."
        ollama pull nomic-embed-text
        echo "export EMBEDDING_MODEL=nomic-embed-text" >> .env
        ;;
    all)
        for model in "${MODELS[@]}"; do
            echo "Pulling $model..."
            ollama pull "$model"
        done
        echo "export EMBEDDING_MODEL=qwen3:8b-instruct-q4_K_M" >> .env
        echo "All models pulled! Default set to qwen3:8b-instruct-q4_K_M"
        ;;
    *)
        echo "Invalid choice. Run script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Embedding model setup complete!"
echo ""
echo "Configuration added to .env:"
echo "  EMBEDDING_MODEL=${EMBEDDING_MODEL:-qwen3:8b-instruct-q4_K_M}"
echo ""
echo "You can change the model in OpenWebUI:"
echo "  Settings → AlphaOmega Pipeline → EMBEDDING_MODEL"
echo ""
echo "To test:"
echo "  python test_embedding_intent.py"