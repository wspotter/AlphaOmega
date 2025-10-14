# AlphaOmega Docker Policy

## Official Policy Statement

**Docker is ONLY approved for the following services:**

1. **ComfyUI** - Image generation service
   - **Reason**: Complex dependencies (PyTorch, ROCm, ONNX, etc.)
   - **Location**: `comfyui_bridge/Dockerfile`
   - **Port**: 8188
   
2. **Chatterbox TTS** - Text-to-speech service
   - **Reason**: Requires Python 3.11+, complex audio libraries
   - **Location**: `tts/Dockerfile.chatterbox`
   - **Port**: 5003

## All Other Services Run Locally

The following services **MUST RUN LOCALLY** (not in Docker):

| Service | Port | Why Local? |
|---------|------|------------|
| **OpenWebUI** | 8080 | Direct Python execution, easier debugging, no Docker overhead |
| **Ollama Vision** | 11434 | Direct GPU access, faster startup, no container isolation |
| **Ollama Reasoning** | 11435 | Direct GPU access, faster startup, no container isolation |
| **Agent-S** | 8001 | Requires host display/input access (X11/Wayland) |
| **mcpart** | 3000 | Direct filesystem access, Node.js simplicity |
| **mcpo** | 8002 | Lightweight Go binary, no dependencies |

## Why This Policy?

### User Preferences
- **Simplicity**: Direct execution without Docker complexity
- **Debugging**: Easier to debug with local processes
- **Performance**: No Docker overhead or network isolation
- **Development**: Faster iteration cycles

### Technical Reasons
- **Agent-S**: Cannot properly access display/input from within Docker
- **mcpart**: Needs direct filesystem access for MCP operations
- **OpenWebUI**: No benefit from containerization, adds complexity
- **Ollama**: Direct GPU access is simpler and faster

## What This Means for Development

### ✅ DO:
- Use `docker-compose.yml` for ComfyUI and Chatterbox only
- Run everything else with local scripts (`./scripts/start.sh`)
- Install Python dependencies in local venv
- Use native binaries (Ollama, mcpo)

### ❌ DON'T:
- Add OpenWebUI to docker-compose.yml
- Create Dockerfiles for Agent-S, mcpart, or other services
- Suggest containerizing anything beyond ComfyUI/Chatterbox
- Reference `host.docker.internal` for local services

## For AI Assistants

If you're an AI assistant working on this codebase:

1. **NEVER** suggest Dockerizing services beyond ComfyUI and Chatterbox
2. **ALWAYS** use local execution patterns for other services
3. **CHECK** this policy before making Docker-related changes
4. **UPDATE** documentation to reflect local-first approach

## docker-compose.yml Structure

The `docker-compose.yml` file should contain:

```yaml
services:
  comfyui:
    # Image generation with ROCm
    
  chatterbox:
    # Text-to-speech
```

That's it. No other services.

## Starting Services

### Docker Services (ComfyUI + Chatterbox)
```bash
docker-compose up -d
```

### Local Services (Everything Else)
```bash
# Use the start script
./scripts/start.sh

# Or manually:
ROCR_VISIBLE_DEVICES=0 ollama serve --host 127.0.0.1:11434 &
ROCR_VISIBLE_DEVICES=1 ollama serve --host 127.0.0.1:11435 &
cd /home/stacy/AlphaOmega && source venv/bin/activate && open-webui serve --port 8080 &
cd agent_s && python server.py &
cd mcpart && npm start &
cd mcpo && go run main.go &
```

## Violation Consequences

If Docker is used for unauthorized services:

1. User frustration (this is their explicit preference)
2. Debugging difficulty (containerization hides issues)
3. Performance impact (unnecessary overhead)
4. Development friction (slower iteration)

## Policy Updates

This policy may only be updated by the repository owner. If you believe a service should be containerized:

1. Document the technical reason (not convenience)
2. Explain why local execution is insufficient
3. Get explicit approval before making changes

---

**Last Updated**: October 14, 2025  
**Policy Owner**: @wspotter  
**Enforcement**: Mandatory for all contributors and AI assistants
