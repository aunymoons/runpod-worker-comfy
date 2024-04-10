import cv2
import numpy as np
from PIL import Image
import torch

# Assuming you have these conversion functions

# PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

# Tensor to PIL
# def tensor2pil(image):
#   return Image.fromarray(np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def tensor2pil(tensor):
    return Image.fromarray(tensor.mul(255).byte().numpy().squeeze(0))

def pil2opencv(pil_image):
    return np.array(pil_image.convert('RGB'))[:, :, ::-1].copy()

class BlobDetectorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "detect_largest_blob"
    CATEGORY = "Image Processing"

    def detect_largest_blob(self, image):
        # Convert tensor to PIL Image (if necessary)
        if isinstance(image, torch.Tensor):
            image = tensor2pil(image)

        # Convert PIL Image to OpenCV format
        image = pil2opencv(image)

        # Now proceed with OpenCV operations
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
        result = cv2.bitwise_and(image, image, mask=mask)

        # Convert result back to tensor
        return (pil2tensor(Image.fromarray(result)),)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "BlobDetectorNode": BlobDetectorNode,
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "BlobDetectorNode": "Blob Detector",
}
