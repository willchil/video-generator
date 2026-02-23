import os
import sys


STORY_NAME = 'sample' # Name of the subdirectory in 'contents' to operate with

# Settings used in the final video generation step
class VideoGeneration:
    FRAME_RATE = 24 # Rendered frames per second
    WIDTH = 1280 # Widght in pixels of the resulting video
    HEIGHT = 720 # Height in pixels of the resulting video
    SUBTITLE_RATIO = 0.3 # Percent height of the screen for captioning
    TEXT_COLOR = 'white' # Color that the captioning text will be rendered in
    BACKGROUND_COLOR = 'rgb(185,128,71)' # Color of the background behind the captioning text
    CHARACTERS_PER_LINE = 75 # Maximum number of characters shown on screen at a time
    CROSSFADE_DURATION = 1 # During of crossfade between images in seconds
    GENERATE_FRAMES = False # Whether to generate a series of frames, or if false, encode the video directly
    FONT_SIZE = 32 # Size of the captioning text
    FONT = 'Arial' # Font of the captioning text
    CODEC = 'libx264' # Codec to encode the final video file with

# Settings used when generating images through the ComfyUI API
class ImageGeneration:
    HOST = '127.0.0.1' # Host address that the API is accessible from
    PORT = 8000 # Port that the API is available through
    WORKFLOW = 'klein9b.json' # Workflow JSON filename relative to workflows/, or an absolute path
    WIDTH = 1280 # Width in pixels of each generated image
    HEIGHT = 720 # Height in pixels of each generated image

# Settings used to generate prompts through a compatible LLM API
class PromptGeneration:
    HOST = '127.0.0.1' # Host address that the API is accessible from
    PORT = 11434 # Port that the API is available through, None for HTTPS
    USE_OLLAMA = True # Whether to use the native Ollama API instead of the OpenAI chat completions API
    MODEL = 'gemma3:27b' # Name of the model to generate the prompts with
    API_KEY = None

# Settings used when adding image annotations to the script
class ScriptAnnotation:
    TARGET_DURATION = 10 # Target duration to show each image when splitting captions, splits captions using a greedy algorithm
    WORDS_PER_MINUTE = 183 # Used to set duration of each scene when durations are not explicitly provided

# Settings for generating TTS clips of script lines with Kokoro
class TTSGeneration:
    VOICE = 'af_heart' # Kokoro voice model, None to skip TTS
    SPEED = 1 # Speed multiplier for the generated audio
    SAMPLE_RATE = 24000 # Sample rate to encode the audio file with

# Settings used to procedurally split a provided story file into a segmented script
class CaptionSplitter:
    MAX_CHARACTERS = 150 # Maximum number of characters that can be displayed in a single caption, will truncate to the last complete sentence

# Settings used to control the story-to-video generation pipeline process
class Pipeline:
    DYNAMICALLY_UNLOAD_OLLAMA = True # Whether to unload the LLM from memory after use, will have no effect if not using Ollama locally
    DYNAMICALLY_UNLOAD_COMFYUI = True # Whether to unload the image diffusion model from memory after use




# The first argument will override STORY_NAME if provided when running
# Pass --clean to delete existing generated files before each step
def _resolve_path(value, default_dir):
    """Resolve a path relative to default_dir, unless it's already absolute."""
    if os.path.isabs(value):
        return value
    return os.path.join(default_dir, value)

args = [a for a in sys.argv[1:] if not a.startswith('-')]
story_name = args[0] if args else STORY_NAME
SOURCE_DIRECTORY = _resolve_path(story_name, 'content')
ImageGeneration.WORKFLOW = _resolve_path(ImageGeneration.WORKFLOW, 'workflows')
CLEAN = '--clean' in sys.argv