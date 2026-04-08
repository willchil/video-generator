import os


STORY_NAME = 'sample'
SOURCE_DIRECTORY = None


# Settings used in the final video generation step
class VideoGeneration:
    FRAME_RATE = 24
    WIDTH = 1280
    HEIGHT = 720
    SUBTITLE_RATIO = 0.3
    TEXT_COLOR = 'white'
    BACKGROUND_COLOR = 'rgb(185,128,71)'
    CHARACTERS_PER_LINE = 75
    CROSSFADE_DURATION = 1
    GENERATE_FRAMES = False
    FONT_SIZE = 32
    FONT = 'Arial'
    CODEC = 'libx264'

# Settings used when generating images through the ComfyUI API
class ImageGeneration:
    HOST = '127.0.0.1'
    PORT = 8000
    WORKFLOW = 'klein9b.json'
    WIDTH = 1280
    HEIGHT = 720

# Settings used to generate prompts through a compatible LLM API
class PromptGeneration:
    HOST = '127.0.0.1'
    PORT = 11434
    USE_OLLAMA = True
    MODEL = 'gemma3:27b'
    API_KEY = None

# Settings used when adding image annotations to the script
class ScriptAnnotation:
    TARGET_DURATION = 10
    WORDS_PER_MINUTE = 183

# Settings for generating TTS clips of script lines with Kokoro
class TTSGeneration:
    VOICE = 'af_heart'
    SPEED = 1
    SAMPLE_RATE = 24000

# Settings used to procedurally split a provided story file into a segmented script
class CaptionSplitter:
    MAX_CHARACTERS = 150

# Settings used to control the story-to-video generation pipeline process
class Pipeline:
    DYNAMICALLY_UNLOAD_OLLAMA = True
    DYNAMICALLY_UNLOAD_COMFYUI = True


def _resolve_path(value, default_dir):
    """Resolve a path relative to default_dir, unless it's already absolute."""
    if os.path.isabs(value):
        return value
    return os.path.join(default_dir, value)


def apply_section(config, section_name, cls):
    """Apply config values from a YAML section to a settings class."""
    section = config.get(section_name, {})
    if not section:
        return
    for key, value in section.items():
        attr_name = key.upper()
        if hasattr(cls, attr_name):
            setattr(cls, attr_name, value)


def load_config(config_path, name_override=None):
    """Load settings from a YAML config file, optionally overriding the story name."""
    global STORY_NAME, SOURCE_DIRECTORY

    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    STORY_NAME = config.get('story_name', STORY_NAME)
    if name_override:
        STORY_NAME = name_override

    SOURCE_DIRECTORY = _resolve_path(STORY_NAME, 'content')

    apply_section(config, 'video_generation', VideoGeneration)
    apply_section(config, 'image_generation', ImageGeneration)
    apply_section(config, 'prompt_generation', PromptGeneration)
    apply_section(config, 'script_annotation', ScriptAnnotation)
    apply_section(config, 'tts_generation', TTSGeneration)
    apply_section(config, 'caption_splitter', CaptionSplitter)
    apply_section(config, 'pipeline', Pipeline)

    ImageGeneration.WORKFLOW = _resolve_path(ImageGeneration.WORKFLOW, 'workflows')
