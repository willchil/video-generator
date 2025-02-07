import base64
import os
import requests
from settings import ImageGeneration
from video import SOURCE_DIRECTORY


def generate_image(prompt: str, name: str):

    url = f'http://{ImageGeneration.HOST}:{ImageGeneration.PORT}'
    payload = {
        "prompt": prompt,
        "steps": ImageGeneration.STEPS,
        "width": ImageGeneration.WIDTH,
        "height": ImageGeneration.HEIGHT,
        "override_settings": {
            'sd_model_checkpoint': ImageGeneration.MODEL,  # this can use to switch sd model
        },
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload).json()
    images = response["images"]

    images_directory = os.path.join(f"{SOURCE_DIRECTORY}", "images")
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    for index, image in enumerate(images):
        filename = name if len(images)==1 else f'{name}-{index}'
        save_path = os.path.join(images_directory, f'{filename}.png')
        with open(save_path, "wb") as file:
            file.write(base64.b64decode(image))


def get_prompts():

    # Read the scene file
    path = os.path.join(SOURCE_DIRECTORY, 'scenes.txt')
    with open(path, 'r', encoding='utf-8') as file:
        scenes = file.readlines()
    scenes = [scene.strip() for scene in scenes if scene.strip()]

    return scenes


def generate_prompt_images():
    for index, scene in enumerate(get_prompts()):
        generate_image(scene, str(index))

if __name__ == "__main__":
    generate_prompt_images()