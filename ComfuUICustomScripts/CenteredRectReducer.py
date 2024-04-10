class CenteredRectReducer:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "x": ("FLOAT", {"default": 0.0, "min": -4096.0, "max": 4096.0, "step": 0.1}),
                "y": ("FLOAT", {"default": 0.0, "min": -4096.0, "max": 4096.0, "step": 0.1}),
                "width": ("FLOAT", {"default": 100.0, "min": 1.0, "max": 4096.0, "step": 0.1}),
                "height": ("FLOAT", {"default": 100.0, "min": 1.0, "max": 4096.0, "step": 0.1}),
                "padding": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 1024.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT")
    FUNCTION = "get_centered_rect"
    CATEGORY = "Geometry"

    def get_centered_rect(self, x, y, width, height, padding):
        # Calculate new width and height considering the padding
        new_width = width + (2 * padding)
        new_height = height + (2 * padding)

        # Calculate new x and y for top-left corner
        # new_x = x + padding
        # new_y = y + padding

        # Uncomment below for other corners if needed
        # For top-right corner
        # new_x = x + width - padding - new_width
        # new_y = y + padding

        # For bottom-left corner
        new_x = x - padding
        new_y = y - padding

        # For bottom-right corner
        # new_x = x + width - padding - new_width
        # new_y = y + height - padding - new_height

        return (new_x, new_y, new_width, new_height)

NODE_CLASS_MAPPINGS = {
    "CenteredRectReducer": CenteredRectReducer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CenteredRectReducer": "Centered Rect Reducer",
}
