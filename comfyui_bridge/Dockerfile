# ComfyUI with ROCm support for AMD MI50 GPUs

FROM rocm/pytorch:latest

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HSA_OVERRIDE_GFX_VERSION=9.0.0 \
    COMFYUI_PORT=8188 \
    COMFYUI_ALLOW_REMOTE_API=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    build-essential \
    python3-venv \
    python3-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir xformers==0.0.22.post7 --extra-index-url https://download.pytorch.org/whl/rocm6.0

# Create writable directories (mounted by docker-compose)
RUN mkdir -p /app/output /app/workflows /app/models

EXPOSE 8188

ENTRYPOINT ["python", "main.py"]
CMD ["--listen", "0.0.0.0", "--port", "8188", "--enable-cors-header"]
