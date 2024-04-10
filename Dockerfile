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

# Install ComfyUI dependencies
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    && pip3 install --no-cache-dir xformers==0.0.21

RUN pip3 install opencv-python-headless

RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0

# Clean up to reduce image size
RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ARG CACHEBUST=1

# Clone ComfyUI repository
RUN git clone https://github.com/aunymoons/ComfyUI.git /comfyui

# Change working directory to ComfyUI
WORKDIR /comfyui

RUN pip3 install -r requirements.txt

# # INSTALLING IMPACT PACK
# WORKDIR /comfyui/custom_nodes

# RUN git clone https://github.com/aunymoons/ComfyUI-Impact-Pack.git /comfyui/custom_nodes/ComfyUI-Impact-Pack

# RUN ls -la

# WORKDIR /comfyui/custom_nodes/ComfyUI-Impact-Pack

# RUN ls -la

# RUN git submodule update --init --recursive

# RUN python3 install.py

# WORKDIR /comfyui/custom_nodes/ComfyUI-Impact-Pack/impact_subpack

# RUN python3 install.py

# # INSTALLING MASQUERADE
# WORKDIR /comfyui/custom_nodes

# RUN git clone https://github.com/aunymoons/masquerade-nodes-comfyui.git /comfyui/custom_nodes/masquerade-nodes-comfyui 

# # INSTALLING WAS NODE SUITE
# WORKDIR /comfyui/custom_nodes

# RUN git clone https://github.com/aunymoons/was-node-suite-comfyui.git /comfyui/custom_nodes/was-node-suite-comfyui

# RUN ls -la

# WORKDIR /comfyui/custom_nodes/was-node-suite-comfyui

# RUN ls -la

# RUN pip install -r requirements.txt

# # INSTALLING CONTROLNET AUXILIARY NODES
# WORKDIR /comfyui/custom_nodes

# RUN git clone https://github.com/aunymoons/comfyui_controlnet_aux.git /comfyui/custom_nodes/comfyui_controlnet_aux

# RUN ls -la

# WORKDIR /comfyui/custom_nodes/comfyui_controlnet_aux

# RUN ls -la

# RUN pip install -r requirements.txt

# # INSTALLING ALLOR
# WORKDIR /comfyui/custom_nodes

# RUN git clone https://github.com/aunymoons/ComfyUI-Allor.git /comfyui/custom_nodes/comfyui-allor

# WORKDIR /comfyui/custom_nodes/comfyui-allor

# RUN pip install -r requirements.txt

# Install runpod
RUN pip3 install runpod requests

# Change working directory to ComfyUI
WORKDIR /

# Download models to include in image. (not required if including other models below)

RUN mkdir -p /comfyui/models/checkpoints
RUN mkdir -p /comfyui/models/configs
RUN mkdir -p /comfyui/models/vae
RUN mkdir -p /comfyui/models/embeddings
RUN mkdir -p /comfyui/models/upscale_models
RUN mkdir -p /comfyui/models/loras
RUN mkdir -p /comfyui/models/controlnet
RUN mkdir -p /comfyui/models/hypernetworks

COPY C:/Users/Aunym/Documents/Repositories/stable-diffusion-webui/models/Stable-diffusion/sd_xl_base_1.0.safetensors /comfyui/models/checkpoints/
COPY stable-diffusion-webui/models/Stable-diffusion/sd_xl_turbo_1.0_fp16.safetensors /comfyui/models/checkpoints/
COPY C:/Users/Aunym/Documents/Repositories/stable-diffusion-webui/models/Stable-diffusion/airfucksBruteMix_v10.safetensors /comfyui/models/checkpoints/
COPY stable-diffusion-webui/models/Stable-diffusion/bb95FurryMix_v60.safetensors /comfyui/models/checkpoints/
COPY stable-diffusion-webui/models/Stable-diffusion/homofidelis_v20BETA.safetensors /comfyui/models/checkpoints/
COPY stable-diffusion-webui/models/Stable-diffusion/crystalClearXL_ccxl.safetensors /comfyui/models/checkpoints/

# Download Controlnets 

COPY stable-diffusion-webui/extensions/sd-webui-controlnet/models/diffusers_xl_depth_full.safetensors /comfyui/models/controlnet/
COPY stable-diffusion-webui/extensions/sd-webui-controlnet/models/control_v11f1p_sd15_depth.pth /comfyui/models/controlnet/
COPY stable-diffusion-webui/extensions/sd-webui-controlnet/models/control_v11p_sd15_inpaint.pth /comfyui/models/controlnet/

# Download Loras to include in image.
COPY stable-diffusion-webui/models/Lora/extreme-low-angle-perspective.safetensors /comfyui/models/loras/
COPY stable-diffusion-webui/models/Lora/tinyman.safetensors /comfyui/models/loras/
COPY stable-diffusion-webui/models/Lora/tinyman512.safetensors /comfyui/models/loras/
# COPY stable-diffusion-webui/models/Lora/lcm_lora_sdxl.safetensors /comfyui/models/loras/
COPY stable-diffusion-webui/models/Lora/BetterCocks2.safetensors /comfyui/models/loras/
COPY stable-diffusion-webui/models/Lora/xpenisv9-000040.safetensors /comfyui/models/loras/


# Download VAEs
COPY stable-diffusion-webui/models/VAE/vae-ft-mse-840000-ema-pruned.safetensors /comfyui/models/vae/
COPY stable-diffusion-webui/models/VAE/sdxl_vae.safetensors /comfyui/models/vae/

# Create necessary directories
RUN mkdir -p /comfyui/models/ultralytics
RUN mkdir -p /comfyui/models/ultralytics/bbox
RUN mkdir -p /comfyui/models/ultralytics/segm
RUN mkdir -p /comfyui/models/sams
RUN mkdir -p /comfyui/models/midas/checkpoints

# Get SAM models
COPY ComfyUI_windows_portable/ComfyUI/models/sams/sam_vit_b_01ec64.pth /comfyui/models/sams/

# Get Ultralytics models
COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/bbox/face_yolov8m.pt /comfyui/models/ultralytics/bbox/
COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/bbox/hand_yolov8s.pt /comfyui/models/ultralytics/bbox/

COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/segm/foot-yolov8l.pt /comfyui/models/ultralytics/segm/
COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/segm/genitalia.pt /comfyui/models/ultralytics/segm/
COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/segm/penisV2.pt /comfyui/models/ultralytics/segm/
COPY ComfyUI_windows_portable/ComfyUI/models/ultralytics/segm/person_yolov8m-seg.pt /comfyui/models/ultralytics/segm/

# Go back to the root
WORKDIR /

# Add the start and the handler
ADD src/start.sh src/rp_handler.py test_input.json ./
RUN chmod +x /start.sh

# Start the container
CMD /start.sh
