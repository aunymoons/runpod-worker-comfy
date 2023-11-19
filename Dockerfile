# Use Nvidia CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

# Prevents prompts from packages asking for user input during installation
ENV DEBIAN_FRONTEND=noninteractive
# Prefer binary wheels over source distributions for faster pip installations
ENV PIP_PREFER_BINARY=1
# Ensures output from python is printed immediately to the terminal without buffering
ENV PYTHONUNBUFFERED=1 

# Install Python, git and other necessary tools
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget

# Clean up to reduce image size
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Clone ComfyUI repository
RUN git clone https://github.com/aunymoons/ComfyUI.git /comfyui

# Change working directory to ComfyUI
WORKDIR /comfyui

# Install ComfyUI dependencies
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    && pip3 install --no-cache-dir xformers==0.0.21 \
    && pip3 install -r requirements.txt

# Install runpod
RUN pip3 install runpod requests

# Download models to include in image. (not required if including other models below)
RUN wget -O models/checkpoints/sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
RUN wget -O models/checkpoints/sdxl_vae.safetensors https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors

# Download Loras to include in image.
RUN wget -O models/loras/extreme-low-angle-perspective.safetensors https://huggingface.co/AunyMoons/loras-pack/resolve/main/extreme-low-angle-perspective.safetensors
RUN wget -O models/loras/tinyman.safetensors https://huggingface.co/AunyMoons/loras-pack/blob/main/tinyman.safetensors

# go to custom nodes to begin installing them
WORKDIR /comfyui/custom_nodes

# INSTALLING IMPACT PACK
RUN git clone https://github.com/aunymoons/ComfyUI-Impact-Pack.git /comfyui/custom_nodes 
WORKDIR /comfyui/custom_nodes/ComfyUI-Impact-Pack
RUN git submodule update --init --recursive && python3 install.py

WORKDIR /comfyui/custom_nodes


# # Example for adding specific models into image
# ADD models/checkpoints/sd_xl_base_1.0.safetensors models/checkpoints/
# ADD models/checkpoints/sdxl_vae.safetensors models/checkpoints/

# Go back to the root
WORKDIR /

# Add the start and the handler
ADD src/start.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh

# Start the container
CMD /start.sh
