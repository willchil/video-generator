from caption_splitter import split_captions
from tts_generator import generate_tts
from script_annotator import annotate_script
from prompt_generator import generate_scenes, unload_ollama_model
from image_generator import generate_prompt_images, unload_diffusion_model
from render_clips import render_clips
from settings import Pipeline


if __name__ == "__main__":
    split_captions()
    generate_tts()
    annotate_script()
    generate_scenes()
    if Pipeline.DYNAMICALLY_UNLOAD_OLLAMA: unload_ollama_model()
    generate_prompt_images()
    if Pipeline.DYNAMICALLY_UNLOAD_COMFYUI: unload_diffusion_model()
    render_clips()