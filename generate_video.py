import glob
import os
import shutil
from caption_splitter import split_captions
from tts_generator import generate_tts
from script_annotator import annotate_script
from prompt_generator import generate_scenes, unload_ollama_model
from image_generator import generate_prompt_images, unload_diffusion_model
from render_clips import render_clips
from settings import Pipeline, SOURCE_DIRECTORY, CLEAN


def files_exist(*paths):
    """Return True if all paths exist (supports glob patterns)."""
    for path in paths:
        if '*' in path or '?' in path:
            if not glob.glob(path):
                return False
        elif not os.path.exists(path):
            return False
    return True


def clean(*paths):
    """Delete files and directories at the given paths (supports glob patterns)."""
    for path in paths:
        targets = glob.glob(path) if ('*' in path or '?' in path) else [path]
        for target in targets:
            if os.path.isdir(target):
                shutil.rmtree(target)
                print(f"  Cleaned {target}/")
            elif os.path.isfile(target):
                os.remove(target)
                print(f"  Cleaned {target}")


def run_step(name, func, output_paths, post=None):
    """Run a pipeline step, skipping if outputs exist."""
    if files_exist(*output_paths):
        print(f"Skipping {name} (files already exist)")
        return
    func()
    if post:
        post()


if __name__ == "__main__":
    captions = os.path.join(SOURCE_DIRECTORY, 'captions.txt')
    audio_dir = os.path.join(SOURCE_DIRECTORY, 'audio')
    script = os.path.join(SOURCE_DIRECTORY, 'script.txt')
    scenes = os.path.join(SOURCE_DIRECTORY, 'scenes.txt')
    images_dir = os.path.join(SOURCE_DIRECTORY, 'images')
    video = os.path.join(SOURCE_DIRECTORY, 'video.mp4')

    all_outputs = [captions, audio_dir, script, scenes, images_dir, video]

    if CLEAN:
        clean(*all_outputs)

    run_step('caption splitting', split_captions, [captions])
    run_step('TTS generation', generate_tts, [audio_dir])
    run_step('script annotation', annotate_script, [script])
    run_step('scene generation', generate_scenes, [scenes],
             post=unload_ollama_model if Pipeline.DYNAMICALLY_UNLOAD_OLLAMA else None)
    run_step('image generation', generate_prompt_images, [images_dir],
             post=unload_diffusion_model if Pipeline.DYNAMICALLY_UNLOAD_COMFYUI else None)
    run_step('video rendering', render_clips, [video])