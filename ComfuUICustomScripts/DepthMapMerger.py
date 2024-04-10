import torch

class DepthMapMerger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "depth_map1": ("IMAGE",),
                "depth_map2": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "merge"
    CATEGORY = "Depth Map"

    def merge(self, depth_map1, depth_map2):
        # Validate tensor shapes
        if depth_map1.shape != depth_map2.shape:
            raise ValueError(f"Depth maps must have the same dimensions. Got {depth_map1.shape} and {depth_map2.shape} instead.")

        # if len(depth_map1.shape) != 2:
        #    raise ValueError("Expected 2D tensors.")

        # Normalize tensors to [0, 1] if necessary
        depth_map1 = depth_map1.float() / 255.0 if depth_map1.max().item() > 1 else depth_map1.float()
        depth_map2 = depth_map2.float() / 255.0 if depth_map2.max().item() > 1 else depth_map2.float()

        # Merge
        output_depth_map = torch.where(depth_map1 > depth_map2, depth_map1, depth_map2)

        return (output_depth_map, )

NODE_CLASS_MAPPINGS = {
    "DepthMapMerger": DepthMapMerger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DepthMapMerger": "Depth Map Merger",
}
