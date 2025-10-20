# ComfyUI Status - October 13, 2025

## Current State
- **Process**: ComfyUI runs locally (not in Docker)
- **Status**: Local Python execution with ROCm GPU support
- **Port**: 8188 (direct local process)
- **GPU**: Assigned to GPU 2 (MI50 #3)

## Configuration
ComfyUI runs as a local Python process with:
- Direct ROCm GPU access for image generation
- SDXL and Flux workflow support
- Local model storage in `./models/comfyui/`
- Workflow configurations in `./comfyui_bridge/workflows/`
- Output directory: `./comfyui_bridge/output/`

## Local Execution
```bash
cd comfyui_bridge
python main.py
```

## Integration Points
- OpenWebUI can route image generation requests to local ComfyUI
- Agent-S can trigger image generation workflows
- All processing happens locally with GPU acceleration
