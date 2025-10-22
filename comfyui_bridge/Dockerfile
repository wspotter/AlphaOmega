# AlphaOmega ComfyUI container with AMD ROCm support
FROM rocm/pytorch:rocm6.2_ubuntu22.04_py3.10_pytorch_release_2.3.0

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    HSA_OVERRIDE_GFX_VERSION=9.0.0

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/ComfyUI

# Clone ComfyUI
RUN git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git /tmp/ComfyUI && \
    mv /tmp/ComfyUI/* /app/ComfyUI && \
    rm -rf /tmp/ComfyUI

# Upgrade PyTorch and install compatible transformers
RUN pip install --upgrade pip setuptools wheel && \
    pip install --upgrade --force-reinstall \
        torch==2.4.0+rocm6.2 \
        torchvision==0.19.0+rocm6.2 \
        torchaudio==2.4.0+rocm6.2 \
        --index-url https://download.pytorch.org/whl/rocm6.2 && \
    pip install transformers==4.44.2 && \
    pip install -r requirements.txt && \
    pip install onnxruntime-rocm>=1.18.0 accelerate>=0.32.0

EXPOSE 8188

CMD ["python", "main.py", "--listen", "--port", "8188"]
