import os
import re
import sys
from typing import List, Tuple
from moviepy import AudioFileClip
from settings import ScriptAnnotation, SOURCE_DIRECTORY


def parse_lines(file: str = 'script') -> List[Tuple[float, str, str]]:

    # Read the script file
    path = os.path.join(SOURCE_DIRECTORY, f'{file}.txt')
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

        # If no duration was found, calculate it based on words count
        if not duration:
            duration = approximate_duration(line)

        result.append((duration, image_name, line))

    return result


def approximate_duration(line: str) -> float:
    words_count = len(re.findall(r'\w+', line))
    return (words_count / ScriptAnnotation.WORDS_PER_MINUTE) * 60


def print_progress_bar(index, total, action):
    n_bar = 50  # Progress bar width
    progress = index / total
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'=' * int(n_bar * progress):{n_bar}s}] {index} / {total} {action}")
    sys.stdout.flush()


def get_audio_clips(count: int):
    audio_clips = [None] * count
    audio_dir = os.path.join(SOURCE_DIRECTORY, 'audio')
    if os.path.isdir(audio_dir):
        for index in range(count):
            audio_file = os.path.join(audio_dir, f'{index}.wav')
            if not os.path.isfile(audio_file): continue
            audio_clip = AudioFileClip(audio_file)
            audio_clips[index] = audio_clip
    return audio_clips