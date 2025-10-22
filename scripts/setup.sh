#!/bin/bash
# AlphaOmega Setup Script
# Configures system, installs dependencies, pulls models

set -e

echo "======================================"
echo "AlphaOmega Setup Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}ERROR: Do not run this script as root${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking system requirements...${NC}"

# Check for ROCm
if ! command -v rocm-smi &> /dev/null; then
    echo -e "${RED}ERROR: ROCm not found. Please install ROCm first.${NC}"
    echo "Visit: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/"
    exit 1
fi

echo -e "${GREEN}✓ ROCm found${NC}"
rocm-smi --showid

echo ""
echo -e "${YELLOW}Step 2: Setting up environment...${NC}"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}Please edit .env to match your GPU configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
mkdir -p logs models/{ollama,comfyui} openwebui_data /tmp/mcp_artifacts /tmp/agent_screenshots
echo -e "${GREEN}✓ Created directories${NC}"

# Create .gitkeep files
touch models/ollama/.gitkeep models/comfyui/.gitkeep

echo ""
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"

# Create virtual environment (optional, for local development)
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 4: Checking Ollama installation...${NC}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi

# Set HSA override for MI50
echo ""
echo -e "${YELLOW}Step 5: Configuring ROCm for MI50 GPUs...${NC}"

if ! grep -q "HSA_OVERRIDE_GFX_VERSION" ~/.bashrc; then
    echo 'export HSA_OVERRIDE_GFX_VERSION=9.0.0' >> ~/.bashrc
    echo -e "${GREEN}✓ Added HSA_OVERRIDE_GFX_VERSION to ~/.bashrc${NC}"
    echo -e "${YELLOW}Run: source ~/.bashrc to apply changes${NC}"
else
    echo -e "${GREEN}✓ HSA_OVERRIDE_GFX_VERSION already set${NC}"
fi

export HSA_OVERRIDE_GFX_VERSION=9.0.0

echo ""
echo -e "${YELLOW}Step 6: Pulling Ollama models (this may take a while)...${NC}"

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    echo -e "${GREEN}✓ Started Ollama service${NC}"
fi

# Pull models
echo "Pulling llava:34b (Vision model - ~20GB)..."
ollama pull llava:34b || echo -e "${YELLOW}Warning: Failed to pull llava:34b${NC}"

echo "Pulling mistral (Reasoning model - ~4GB)..."
ollama pull mistral || echo -e "${YELLOW}Warning: Failed to pull mistral${NC}"

echo "Pulling codellama:13b (Code model - ~7GB)..."
ollama pull codellama:13b || echo -e "${YELLOW}Warning: Failed to pull codellama:13b${NC}"

echo -e "${GREEN}✓ Models pulled successfully${NC}"

echo ""
echo "======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your specific configuration"
echo "2. Start services: ./scripts/start.sh"
echo "3. Access OpenWebUI at http://localhost:8080"
echo ""
echo "For development:"
echo "  - Agent-S API: http://localhost:8001"
echo "  - Ollama Vision: http://localhost:11434"
echo "  - Ollama Reasoning: http://localhost:11435"
echo "  - ComfyUI: http://localhost:8188"
echo "  - MCP Tool Server: http://localhost:8002/openapi.json"
echo ""
