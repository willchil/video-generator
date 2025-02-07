
STORY_NAME = 'sample' # Name of the subdirectory in 'contents' to operate with

# Settings used in the final video generation step
class VideoGeneration:
    FRAME_RATE = 4 # Rendered frames per second
    WIDTH = 1280 # Widght in pixels of the resulting video
    HEIGHT = 720 # Height in pixels of the resulting video
    SUBTITLE_RATIO = 0.3 # Percent height of the screen for captioning
    TEXT_COLOR = 'white' # Color that the captioning text will be rendered in
    BACKGROUND_COLOR = 'rgb(185,128,71)' # Color of the background behind the captioning text
    WORDS_PER_MINUTE = 183 # Used to set duration of each scene with durations are not explicitly provided
    CHARACTERS_PER_LINE = 75 # Maximum number of characters shown on screen at a time
    CROSSFADE_DURATION = 1 # During of crossfade between images in seconds
    GENERATE_FRAMES = False # Whether to generate a series of frames, or if false, encode the video directly
    FONT_SIZE = 32 # Size of the captioning text
    FONT = 'Arial' # Font of the captioning text
    CODEC = 'libx264' # Codec to encode the final video file with

# Settings used to procedurally split a provided story file into a segmented script
class ScriptSplitter:
    MAX_CHARACTERS = 300 # Maximum number of characters that can be displayed in a single caption, will truncate to the last complete sentence
    TARGET_DURATION = 15 # Target duration to show each image when splitting captions, splits captions using a greedy algorithm

# Settings used when generating images through the AUTOMATIC1111 (or Forge) txt2img API
class ImageGeneration:
    HOST = '127.0.0.1' # Host address that the API is accessible from
    PORT = 7860 # Port that the API is available through
    STEPS = 20 # Number of diffusion steps to generate each image for
    WIDTH = 1280 # Width in pixels of each generated image
    HEIGHT = 720 # Height in pixels of each generated image
    MODEL = 'sdxl' # Name of model to use with AUTOMATIC1111

# Settings used to generate prompts through a service compatible with the OpenAI chat completions API
class PromptGeneration:
    HOST = '127.0.0.1' # Host address that the API is accessible from
    PORT = 11434 # Port that the API is available through
    MODEL = 'mistral-small:24b' # Name of the model to generate the prompts with