from script_splitter import generate_script
from tts_generator import generate_tts
from prompt_generator import generate_scenes, unload_ollama_model
from image_generator import generate_prompt_images, unload_diffusion_model
from render_clips import render_clips
from settings import Pipeline


if __name__ == "__main__":
    generate_script()
    generate_tts()
    generate_scenes()
    if Pipeline.DYNAMICALLY_UNLOAD_OLLAMA: unload_ollama_model()
    generate_prompt_images()
    if Pipeline.DYNAMICALLY_UNLOAD_AUTOMATIC1111: unload_diffusion_model()
    render_clips()