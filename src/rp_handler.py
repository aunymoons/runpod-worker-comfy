import runpod
from runpod.serverless.utils import rp_upload
import json
import urllib.request
import urllib.parse
import time
import os
import requests
import base64

# Time to wait between API check attempts in milliseconds
COMFY_API_AVAILABLE_INTERVAL_MS = 1000
# Maximum number of API check attempts
COMFY_API_AVAILABLE_MAX_RETRIES = 60
# Time to wait between poll attempts in milliseconds
COMFY_POLLING_INTERVAL_MS = 1000
# Maximum number of poll attempts
COMFY_POLLING_MAX_RETRIES = 90
# Host where ComfyUI is running
COMFY_HOST = "127.0.0.1:8188"
# The path where ComfyUI stores the generated images
COMFY_OUTPUT_PATH = "/comfyui/output"


def check_server(url, retries=50, delay=500):
    """
    Check if a server is reachable via HTTP GET request

    Args:
    - url (str): The URL to check
    - retries (int, optional): The number of times to attempt connecting to the server. Default is 50
    - delay (int, optional): The time in milliseconds to wait between retries. Default is 500

    Returns:
    bool: True if the server is reachable within the given number of retries, otherwise False
    """

    for i in range(retries):
        try:
            response = requests.get(url)
            # If the response status code is 200, the server is up and running
            if response.status_code == 200:
                print(f"runpod-worker-comfy - API is reachable")
                return True
        except requests.RequestException as e:
            # If an exception occurs, the server may not be ready
            pass

        # Wait for the specified delay before retrying
        time.sleep(delay / 1000)

    print(
        f"runpod-worker-comfy - Failed to connect to server at {url} after {retries} attempts."
    )
    return False


def queue_prompt(prompt):
    """
    Queue a prompt to be processed by ComfyUI

    Args:
        prompt (dict): A dictionary containing the prompt to be processed

    Returns:
        dict: The JSON response from ComfyUI after processing the prompt
    """
    data = json.dumps(prompt).encode("utf-8")
    req = urllib.request.Request(f"http://{COMFY_HOST}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_history(prompt_id):
    """
    Retrieve the history of a given prompt using its ID

    Args:
        prompt_id (str): The ID of the prompt whose history is to be retrieved

    Returns:
        dict: The history of the prompt, containing all the processing steps and results
    """
    with urllib.request.urlopen(f"http://{COMFY_HOST}/history/{prompt_id}") as response:
        return json.loads(response.read())


def base64_encode(img_path):
    """
    Returns base64 encoded image.
    """
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")
    

def handler(job):
    """
    The main function that handles a job of generating an image.

    This function validates the input, sends a prompt to ComfyUI for processing,
    polls ComfyUI for result, and retrieves generated images.

    Args:
        job (dict): A dictionary containing job details and input parameters.

    Returns:
        dict: A dictionary containing either an error message or a success status with generated images.
    """
    job_input = job["input"]

    # Make sure that the ComfyUI API is available
    check_server(
        f"http://{COMFY_HOST}",
        COMFY_API_AVAILABLE_MAX_RETRIES,
        COMFY_API_AVAILABLE_INTERVAL_MS,
    )

    # Validate input
    if job_input is None:
        return {"error": "Please provide the 'prompt'"}

    # Is JSON?
    if isinstance(job_input, dict):
        prompt = job_input
    # Is String?
    elif isinstance(job_input, str):
        try:
            prompt = json.loads(job_input)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in 'prompt'"}
    else:
        return {"error": "'prompt' must be a JSON object or a JSON-encoded string"}

    # Queue the prompt
    try:
        queued_prompt = queue_prompt(prompt)
        prompt_id = queued_prompt["prompt_id"]
        print(f"runpod-worker-comfy - queued prompt with ID {prompt_id}")
    except Exception as e:
        return {"error": f"Error queuing prompt: {str(e)}"}

    # Poll for completion
    print(f"runpod-worker-comfy - wait until image generation is complete")
    retries = 0
    try:
        while retries < COMFY_POLLING_MAX_RETRIES:
            history = get_history(prompt_id)

            # Exit the loop if we have found the history
            if prompt_id in history and history[prompt_id].get("outputs"):
                break
            else:
                # Wait before trying again
                time.sleep(COMFY_POLLING_INTERVAL_MS / 1000)
                retries += 1
        else:
            return {"error": "Max retries reached while waiting for image generation"}
    except Exception as e:
        return {"error": f"Error waiting for image generation: {str(e)}"}

    # Fetching generated images
    output_images = {}

    outputs = history[prompt_id].get("outputs")

    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for image in node_output["images"]:
                output_images = image["filename"]

    print(f"runpod-worker-comfy - image generation is done")

    # expected image output folder
    local_image_path = f"{COMFY_OUTPUT_PATH}/{output_images}"
    print(f"Local image path is: {local_image_path}")
    # The image is in the output folder
    if os.path.exists(local_image_path):
        print("runpod-worker-comfy - the image exists in the output folder")
        print("Auny's version")
        image_url = rp_upload.upload_image(job["id"], local_image_path)
        return_base64 = "simulated_uploaded/" in image_url
        return_output = f"{image_url}" if not return_base64 else base64_encode(local_image_path)
        return {
            "status": "success", 
            "message": return_output, 
        }
    else:
        print("runpod-worker-comfy - the image does not exist in the output folder")
        return {
            "status": "error",
            "message": f"the image does not exist in the specified output folder: {local_image_path}",
        }


# Start the handler
runpod.serverless.start({"handler": handler})
