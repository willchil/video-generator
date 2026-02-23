import json
import os
import random
import uuid
import urllib.parse
import urllib.request
import websocket
from utility import print_progress_bar
from settings import ImageGeneration, SOURCE_DIRECTORY


def get_base_url():
    return f"http://{ImageGeneration.HOST}:{ImageGeneration.PORT}"


def get_ws_url(client_id):
    return f"ws://{ImageGeneration.HOST}:{ImageGeneration.PORT}/ws?clientId={client_id}"


def load_workflow():
    """Load the ComfyUI workflow from the configured JSON file."""
    with open(ImageGeneration.WORKFLOW, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_nodes_by_class(workflow, class_type):
    """Find all node IDs with the given class_type."""
    return [nid for nid, node in workflow.items() if node.get("class_type") == class_type]


def find_nodes_by_title(workflow, title):
    """Find all node IDs whose _meta.title matches the given title."""
    return [nid for nid, node in workflow.items()
            if node.get("_meta", {}).get("title") == title]


def configure_workflow(workflow, prompt, width, height):
    """Configure the workflow with the given prompt text and image dimensions."""

    # Set the prompt text on CLIPTextEncode nodes that have a direct string text input
    for node_id in find_nodes_by_class(workflow, "CLIPTextEncode"):
        if isinstance(workflow[node_id]["inputs"].get("text"), str):
            workflow[node_id]["inputs"]["text"] = prompt

    # Set the prompt text on PrimitiveStringMultiline nodes (used as prompt sources)
    for node_id in find_nodes_by_class(workflow, "PrimitiveStringMultiline"):
        if "value" in workflow[node_id]["inputs"]:
            workflow[node_id]["inputs"]["value"] = prompt

    # Set dimensions on latent image nodes with direct integer inputs
    for class_type in ["EmptySD3LatentImage", "EmptyLatentImage", "EmptyFlux2LatentImage"]:
        for node_id in find_nodes_by_class(workflow, class_type):
            inputs = workflow[node_id]["inputs"]
            if isinstance(inputs.get("width"), int):
                inputs["width"] = width
            if isinstance(inputs.get("height"), int):
                inputs["height"] = height

    # Set dimensions on PrimitiveInt nodes titled "Width" or "Height"
    for node_id in find_nodes_by_title(workflow, "Width"):
        if workflow[node_id]["class_type"] == "PrimitiveInt":
            workflow[node_id]["inputs"]["value"] = width
    for node_id in find_nodes_by_title(workflow, "Height"):
        if workflow[node_id]["class_type"] == "PrimitiveInt":
            workflow[node_id]["inputs"]["value"] = height

    # Randomize seed on KSampler nodes
    for node_id in find_nodes_by_class(workflow, "KSampler"):
        workflow[node_id]["inputs"]["seed"] = random.randint(0, 2**63)

    # Randomize seed on RandomNoise nodes
    for node_id in find_nodes_by_class(workflow, "RandomNoise"):
        workflow[node_id]["inputs"]["noise_seed"] = random.randint(0, 2**63)

    return workflow


def queue_prompt(workflow, client_id):
    """Queue a prompt with ComfyUI and return the prompt_id."""
    url = f"{get_base_url()}/prompt"
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())["prompt_id"]


def wait_for_completion(ws, prompt_id):
    """Listen on the WebSocket until the given prompt finishes executing."""
    while True:
        message = ws.recv()
        if isinstance(message, str):
            data = json.loads(message)
            if data.get("type") == "executing":
                exec_data = data.get("data", {})
                if exec_data.get("prompt_id") == prompt_id and exec_data.get("node") is None:
                    return


def get_history(prompt_id):
    """Fetch the execution history for a completed prompt."""
    url = f"{get_base_url()}/history/{prompt_id}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())[prompt_id]


def download_image(filename, subfolder="", image_type="output"):
    """Download a generated image from ComfyUI's /view endpoint."""
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": image_type})
    url = f"{get_base_url()}/view?{params}"
    with urllib.request.urlopen(url) as response:
        return response.read()


def generate_image(prompt: str, name: str, ws, client_id):
    """Generate a single image using the ComfyUI workflow and save it locally."""
    workflow = load_workflow()
    workflow = configure_workflow(workflow, prompt, ImageGeneration.WIDTH, ImageGeneration.HEIGHT)

    prompt_id = queue_prompt(workflow, client_id)
    wait_for_completion(ws, prompt_id)
    history = get_history(prompt_id)

    # Extract the output image from the execution history
    outputs = history.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for image_info in node_output["images"]:
                image_data = download_image(
                    image_info["filename"],
                    image_info.get("subfolder", "")
                )
                images_directory = os.path.join(SOURCE_DIRECTORY, "images")
                os.makedirs(images_directory, exist_ok=True)
                save_path = os.path.join(images_directory, f"{name}.png")
                with open(save_path, "wb") as f:
                    f.write(image_data)
                return  # Save only the first image


def unload_diffusion_model():
    """Free GPU memory by unloading models in ComfyUI."""
    url = f"{get_base_url()}/free"
    data = json.dumps({"unload_models": True, "free_memory": True}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
    except Exception:
        pass


def get_prompts():

    # Read the scene file
    path = os.path.join(SOURCE_DIRECTORY, 'scenes.txt')
    with open(path, 'r', encoding='utf-8') as file:
        scenes = file.readlines()
    scenes = [scene.strip() for scene in scenes if scene.strip()]

    return scenes


def generate_prompt_images():
    prompts = get_prompts()
    count = len(prompts)
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()
    ws.connect(get_ws_url(client_id))
    try:
        for index, scene in enumerate(prompts):
            print_progress_bar(index, count, "images generated")
            generate_image(scene, str(index), ws, client_id)
        print_progress_bar(count, count, "images generated\n")
    finally:
        ws.close()


if __name__ == "__main__":
    generate_prompt_images()