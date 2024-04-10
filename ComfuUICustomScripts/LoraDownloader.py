import requests
from PIL import Image
from io import BytesIO
import torch
import numpy as np

# PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

class LoraDownloader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_url": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "download"
    CATEGORY = "Image Processing"

    def download(self, image_url):
        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            pil_img = Image.open(BytesIO(response.content))

            # Convert PIL Image to tensor
            image_tensor = pil2tensor(pil_img)
            return (image_tensor,)
        else:
            raise Exception(f"Failed to download image: HTTP {response.status_code}")

NODE_CLASS_MAPPINGS = {
    "LoraDownloader": LoraDownloader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraDownloader": "LORA Downloader",
}
