# ComfyUI Status - October 13, 2025

## Current State
- **Container**: `alphaomega-comfyui` exists but failing to start
- **Error**: PyTorch/transformers compatibility issue
  ```
  AttributeError: module 'torch.utils._pytree' has no attribute 'register_pytree_node'
  ```
- **Port**: 8188 (configured in docker-compose.yml)
- **GPU**: Assigned to GPU 2 (MI50 #3)

## Issue
The existing ComfyUI container has incompatible Python dependencies:
- PyTorch version conflicts with transformers library
- Needs rebuild with compatible versions

## Resolution Needed
1. Create new Dockerfile for ComfyUI with ROCm support
2. Install compatible PyTorch + transformers versions
3. Rebuild image and restart container

## Docker-Compose Config
```yaml
comfyui:
  build:
    context: ./comfyui_bridge
  container_name: alphaomega-comfyui
  ports:
    - "8188:8188"
  volumes:
    - ./models/comfyui:/app/models
    - ./comfyui_bridge/workflows:/app/workflows
    - ./comfyui_bridge/output:/app/output
```

## Next Steps
- Build ComfyUI Dockerfile with proper dependencies
- Test with SDXL/Flux workflows
- Document image generation endpoints

---
*Deferred pending TTS completion - User priority: TTS first, then ComfyUI*
