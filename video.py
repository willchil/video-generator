import os
import re
import textwrap
from typing import List, Tuple
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, VideoClip, ImageSequenceClip, concatenate_videoclips
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from settings import VideoGeneration, STORY_NAME


SOURCE_DIRECTORY = os.path.join('content', STORY_NAME)

def parse_lines() -> List[Tuple[float, str, str]]:

    # Read the script file
    path = os.path.join(SOURCE_DIRECTORY, 'script.txt')
    with open(path, 'r', encoding='utf-8') as file:
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
    return (words_count / VideoGeneration.WORDS_PER_MINUTE) * 60


def generate_image_clip(rows: List[Tuple[float, str, str]]) -> VideoClip:

    image_clips = []
    total_duration = 0

    def pan_position(length):
        return lambda t: ('center', (-t / length) * (VideoGeneration.HEIGHT * VideoGeneration.SUBTITLE_RATIO))

    for i in range(len(rows)):
        duration, image_name, _ = rows[i]

        if image_name:

            j = i + 1
            while j < len(rows) and not rows[j][1]:
                duration += rows[j][0]
                j += 1

            # Total duration, accounting for crossfade
            fade_duration = duration + VideoGeneration.CROSSFADE_DURATION

            # Create an image clip
            image_path = f'{SOURCE_DIRECTORY}/images/{image_name}'
            if not image_path.endswith(".png"):
                image_path += ".png"
            image_clip: VideoClip = ImageClip(image_path)
            image_clip = image_clip.with_duration(fade_duration)
            image_clip = image_clip.with_position(('center', 'center'))
            image_clip = image_clip.resized(height=VideoGeneration.HEIGHT)

            # Apply pan effect
            image_clip = image_clip.with_position(pan_position(length=fade_duration))
            image_clip = image_clip.with_start(total_duration)

            # Apply cross fade
            if i > 0:
                image_clip = image_clip.with_effects([CrossFadeIn(VideoGeneration.CROSSFADE_DURATION)])

            # Add the image clip to the list
            image_clips.append(image_clip)

            # Update the total duration
            total_duration += duration

    # Concatenate all image clips with crossfade transition
    final_image_clip = CompositeVideoClip(image_clips)
    final_image_clip = final_image_clip.with_duration(total_duration)

    return final_image_clip


def generate_subtitle_clip(rows: List[Tuple[float, str, str]]) -> VideoClip:
    # Initialize a list to hold all subtitle clips
    subtitle_clips = []

    height = int(VideoGeneration.HEIGHT * VideoGeneration.SUBTITLE_RATIO)
    for duration, _, text in rows:
        # Create a text clip for the subtitle
        text = textwrap.fill(text, VideoGeneration.CHARACTERS_PER_LINE)
        subtitle_clip = TextClip(
            text=text,
            font=VideoGeneration.FONT,
            font_size=VideoGeneration.FONT_SIZE,
            color=VideoGeneration.TEXT_COLOR,
            bg_color=VideoGeneration.BACKGROUND_COLOR,
            size=(VideoGeneration.WIDTH, height)
        )
        subtitle_clip = subtitle_clip.with_duration(duration)

        # Add the subtitle clip to the list
        subtitle_clips.append(subtitle_clip)

    # Concatenate all subtitle clips into one
    final_subtitle_clip = concatenate_videoclips(subtitle_clips, method="chain")
    final_subtitle_clip = final_subtitle_clip.with_position(('center', VideoGeneration.HEIGHT - height))

    return final_subtitle_clip


def video_from_sequence(directory) -> VideoClip:
    frames = sorted([os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png")])
    return ImageSequenceClip(frames, fps=VideoGeneration.FRAME_RATE)


def generate_video(filename: str = 'video'):
    # Generate image and subtitle clips
    lines = parse_lines()
    print("Lines parsed...")
    image_clip = generate_image_clip(lines)
    print("Image clip generated...")
    subtitle_clip = generate_subtitle_clip(lines)
    print("Subtitle clip generated...")

    # Calculate the total duration of all lines
    total_duration = sum(line[0] for line in lines)

    # Write final video clip
    final_video = CompositeVideoClip([image_clip, subtitle_clip], size=(VideoGeneration.WIDTH, VideoGeneration.HEIGHT))
    final_video = final_video.with_duration(total_duration)

    # Add the audio if available, truncated to the total length
    audio_path = os.path.join(SOURCE_DIRECTORY, 'audio.mp3')
    if os.path.isfile(audio_path):
        final_audio = AudioFileClip(audio_path).subclip(0, total_duration)
        final_video = final_video.set_audio(final_audio)

    # Write the final video file or frames
    if VideoGeneration.GENERATE_FRAMES:
        frames_dir = os.path.join(SOURCE_DIRECTORY, 'frames')
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)
        frames_path = os.path.join(frames_dir, 'frame%06d.png')
        final_video.write_images_sequence(frames_path, fps=VideoGeneration.FRAME_RATE)
    else:
        video_path = os.path.join(SOURCE_DIRECTORY, f'{filename}.mp4')
        final_video.write_videofile(video_path, fps=VideoGeneration.FRAME_RATE, codec=VideoGeneration.CODEC, threads=32)

if __name__ == "__main__":
    generate_video("video-temp")