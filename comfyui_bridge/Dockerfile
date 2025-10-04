# ComfyUI Dockerfile with ROCm support
FROM rocm/pytorch:rocm6.0_ubuntu20.04_py3.9_pytorch_2.1.1

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git . && \
    pip install --no-cache-dir -r requirements.txt

# Install additional nodes (optional)
# RUN cd custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# Create directories
RUN mkdir -p /app/models /app/output /app/input /app/workflows

# Expose port
EXPOSE 8188

# Run ComfyUI
CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
