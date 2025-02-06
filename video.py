import re
import os
import textwrap
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoClip, ImageSequenceClip
from typing import List, Tuple

# Constants
TEXT_COLOR = 'white'
BACKGROUND_COLOR = 'rgb(185,128,71)'
WIDTH = 1920
HEIGHT = 1080
FRAME_RATE = 4
SUBTITLE_RATIO = 0.3
WORDS_PER_MINUTE = 183 # for duration estimation
CHARACTERS_PER_LINE = 75
CROSSFADE_DURATION = 1  # seconds
SOURCE_DIRECTORY = 'story'



def parse_lines() -> List[Tuple[float, str, str]]:

    # Read the script file
    with open(f'{SOURCE_DIRECTORY}/script.txt', 'r', encoding='utf-8') as file:
        script_lines = file.readlines()

    script_lines = [line.strip() for line in script_lines if line.strip()]

    result: List[Tuple[float, str, str]] = []

    for line in script_lines:
        # Initialize variables
        image_name = None
        duration = None

        # Check for image name and duration at the start of the line
        matches = re.findall(r'\[([^\]]+)\]', line)
        for match in matches:
            try:
                # If it can be parsed as a float, it's a duration
                duration = float(match)
            except ValueError:
                # Otherwise, it's an image name
                image_name = match
            line = line.replace(f'[{match}]', '', 1)  # Remove the tag from the line
        line = line.strip()
        if ("<end>" in line): # End early if delimiter string detected
            return result

        # If no duration was found, calculate it based on words count
        if not duration:
            duration = approximate_duration(line)

        result.append((duration, image_name, line))

    return result


def approximate_duration(line: str) -> float:
    words_count = len(re.findall(r'\w+', line))
    return (words_count / WORDS_PER_MINUTE) * 60


def generate_image_clip(rows: List[Tuple[float, str, str]]) -> VideoClip:

    image_clips = []
    total_duration = 0

    def pan_position(length):
        return lambda t: ('center', (-t / length) * (HEIGHT * SUBTITLE_RATIO))

    for i in range(len(rows)):
        duration, image_name, _ = rows[i]

        if image_name:

            j = i + 1
            while j < len(rows) and not rows[j][1]:
                duration += rows[j][0]
                j += 1

            # Total duration, accounting for crossfade
            fade_duration = duration + CROSSFADE_DURATION

            # Create an image clip
            image_path = f'{SOURCE_DIRECTORY}/images/{image_name}'
            if not image_path.endswith(".png"):
                image_path += ".png"
            image_clip: VideoClip = ImageClip(image_path)
            image_clip = image_clip.set_duration(fade_duration)
            image_clip = image_clip.set_position(('center', 'center'))
            image_clip = image_clip.resize(height=HEIGHT)

            # Apply pan effect
            image_clip = image_clip.set_position(pan_position(length=fade_duration))
            image_clip = image_clip.set_start(total_duration)

            # Apply cross fade
            if i > 0:
                image_clip = image_clip.crossfadein(CROSSFADE_DURATION)

            # Add the image clip to the list
            image_clips.append(image_clip)

            # Update the total duration
            total_duration += duration

    # Concatenate all image clips with crossfade transition
    final_image_clip = CompositeVideoClip(image_clips)
    final_image_clip = final_image_clip.set_duration(total_duration)

    return final_image_clip


def generate_subtitle_clip(rows: List[Tuple[float, str, str]]) -> VideoClip:
    # Initialize a list to hold all subtitle clips
    subtitle_clips = []

    height = int(HEIGHT * SUBTITLE_RATIO)
    for duration, _, text in rows:
        # Create a text clip for the subtitle
        text = textwrap.fill(text, CHARACTERS_PER_LINE)
        subtitle_clip = TextClip(text, font='Calibri', fontsize=48, color=TEXT_COLOR, bg_color=BACKGROUND_COLOR, size=(WIDTH, height))
        subtitle_clip = subtitle_clip.set_duration(duration)

        # Add the subtitle clip to the list
        subtitle_clips.append(subtitle_clip)

    # Concatenate all subtitle clips into one
    final_subtitle_clip = concatenate_videoclips(subtitle_clips, method="chain")
    final_subtitle_clip = final_subtitle_clip.set_position(('center', HEIGHT - height))

    return final_subtitle_clip


def video_from_sequence(directory) -> VideoClip:
    frames = sorted([os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png")])
    return ImageSequenceClip(frames, fps=FRAME_RATE)


def generate_video(filename: str = "output"):
    # Generate image and subtitle clips
    lines = parse_lines()
    print("Lines parsed...")
    image_clip = generate_image_clip(lines)
    print("Image clip generated...")
    subtitle_clip = generate_subtitle_clip(lines)
    print("Subtitle clip generated...")

    # Calculate the total duration of all lines
    total_duration = sum(line[0] for line in lines)

    # Write final video with audio
    final_video = CompositeVideoClip([image_clip, subtitle_clip], size=(WIDTH, HEIGHT))
    final_video = final_video.set_duration(total_duration)
    #final_video = generate_video(f'{SOURCE_DIRECTORY}/frames')

    # Add the audio, truncated to the total length
    audio_path = f'{SOURCE_DIRECTORY}/audio.mp3'
    if os.path.isfile(audio_path):
        final_audio = AudioFileClip(audio_path).subclip(0, total_duration)
        final_video = final_video.set_audio(final_audio)

    # Write the final video file
    final_video.write_videofile(f'{SOURCE_DIRECTORY}/{filename}.mp4', fps=FRAME_RATE, codec='hevc_nvenc', threads=32)
    #final_video.write_images_sequence(f'{SOURCE_DIRECTORY}/frames/frame%05d.png', fps=FRAME_RATE)

if __name__ == "__main__":
    generate_video("output-temp")