from video import SOURCE_DIRECTORY
import requests
import base64
import os


images_directory = os.path.join(f"{SOURCE_DIRECTORY}", "images")


def generate_image(prompt: str, name: str):

    url = "http://127.0.0.1:7861"
    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 1280,
        "height": 720,
        # "width": 1024,
        # "height": 1024,
        "override_settings": {
            'sd_model_checkpoint': "dynavisionXLAllInOneStylized_release0557Bakedvae",  # this can use to switch sd model
        },
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload).json()

    images = response["images"]
    for index, image in enumerate(images):
        file_name = name if len(images)==1 else f'{name}-{index}'
        save_path = os.path.join(images_directory, f'{file_name}.png')
        with open(save_path, "wb") as file:
            file.write(base64.b64decode(image))


def get_prompts():

    # Read the scene file
    with open(f'{SOURCE_DIRECTORY}/scenes.txt', 'r', encoding='utf-8') as file:
        scenes = file.readlines()
    scenes = [scene.strip() for scene in scenes if scene.strip()]

    return scenes


def generate_prompt_images():
    for index, scene in enumerate(get_prompts()):
        generate_image(scene, str(index))

if __name__ == "__main__":
    generate_prompt_images()