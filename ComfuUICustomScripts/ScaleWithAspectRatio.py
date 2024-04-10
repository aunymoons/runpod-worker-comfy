from PIL import Image
import torch
import numpy as np

# PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

# Tensor to PIL
def tensor2pil(image):
    return Image.fromarray(np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

class AspectRatioScale:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "max_width": ("INT", {"default": 1024, "min": 1, "max": 4096, "step": 1}),
                "max_height": ("INT", {"default": 1024, "min": 1, "max": 4096, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "scale"
    CATEGORY = "Image Processing"

    def scale(self, image, max_width, max_height):
        # Convert tensor to PIL Image
        pil_img = tensor2pil(image)

        # Get original dimensions
        orig_width, orig_height = pil_img.size
        aspect_ratio = orig_width / orig_height

        # Calculate new dimensions
        new_width = min(max_width, int(max_height * aspect_ratio))
        new_height = min(max_height, int(max_width / aspect_ratio))

        # Rescale image
        pil_img_rescaled = pil_img.resize((new_width, new_height), Image.BILINEAR)

        # Convert back to tensor
        image_rescaled = pil2tensor(pil_img_rescaled)

        return (image_rescaled, )

NODE_CLASS_MAPPINGS = {
    "AspectRatioScale": AspectRatioScale,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioScale": "Aspect Ratio Scale",
}