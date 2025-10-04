#!/bin/bash
# Monitor GPU usage and service status

watch -n 1 '
echo "=== GPU Status (rocm-smi) ==="
rocm-smi --showuse --showmeminfo vram 2>/dev/null || echo "ROCm not available"

echo ""
echo "=== Ollama Models Loaded ==="
curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o "\"name\":\"[^\"]*\"" || echo "GPU 0 (Vision): Not responding"
curl -s http://localhost:11435/api/tags 2>/dev/null | grep -o "\"name\":\"[^\"]*\"" || echo "GPU 1 (Reasoning): Not responding"

echo ""
echo "=== Docker Services ==="
docker-compose ps 2>/dev/null || echo "Docker Compose not running"

echo ""
echo "=== Service Health ==="
echo -n "OpenWebUI: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "Down"
echo -n " | Agent-S: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "Down"
echo -n " | ComfyUI: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8188 2>/dev/null || echo "Down"
echo -n " | MCP: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health 2>/dev/null || echo "Down"
echo ""
'
