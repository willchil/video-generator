import argparse
import glob
import os
import shutil
import settings


def resolve_config_path(config_arg):
    """Resolve a config path: absolute paths used as-is, relative paths resolved to configs/."""
    if os.path.isabs(config_arg):
        return config_arg
    return os.path.join('configs', config_arg)


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
    parser = argparse.ArgumentParser(description='Generate a video from a story using AI.')
    parser.add_argument('config', help='Config file path (relative to configs/ or absolute)')
    parser.add_argument('-n', '--name', help='Override the story name from the config')
    parser.add_argument('--clean', action='store_true', help='Delete existing generated files before each step')
    args = parser.parse_args()

    config_path = resolve_config_path(args.config)
    settings.load_config(config_path, name_override=args.name)

    from caption_splitter import split_captions
    from tts_generator import generate_tts
    from script_annotator import annotate_script
    from prompt_generator import generate_scenes, unload_ollama_model
    from image_generator import generate_prompt_images, unload_diffusion_model
    from render_clips import render_clips

    captions = os.path.join(settings.SOURCE_DIRECTORY, 'captions.txt')
    audio_dir = os.path.join(settings.SOURCE_DIRECTORY, 'audio')
    script = os.path.join(settings.SOURCE_DIRECTORY, 'script.txt')
    scenes = os.path.join(settings.SOURCE_DIRECTORY, 'scenes.txt')
    images_dir = os.path.join(settings.SOURCE_DIRECTORY, 'images')
    video = os.path.join(settings.SOURCE_DIRECTORY, 'video.mp4')

    all_outputs = [captions, audio_dir, script, scenes, images_dir, video]

    if args.clean:
        clean(*all_outputs)

    run_step('caption splitting', split_captions, [captions])
    run_step('TTS generation', generate_tts, [audio_dir])
    run_step('script annotation', annotate_script, [script])
    run_step('scene generation', generate_scenes, [scenes],
             post=unload_ollama_model if settings.Pipeline.DYNAMICALLY_UNLOAD_OLLAMA else None)
    run_step('image generation', generate_prompt_images, [images_dir],
             post=unload_diffusion_model if settings.Pipeline.DYNAMICALLY_UNLOAD_COMFYUI else None)
    run_step('video rendering', render_clips, [video])
