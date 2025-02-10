import os
import soundfile as sf
from kokoro import KPipeline
from prompt_generator import print_progress_bar
from settings import TTSGeneration, SOURCE_DIRECTORY
from render_clips import parse_lines


def generate_tts():

    # Make the audio directory if necessary
    audio_dir = os.path.join(SOURCE_DIRECTORY, 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    # Get an ordered list of the lines
    lines = [item[2] for item in parse_lines()]

    # Generate and save audio files in a loop.
    pipeline = KPipeline(lang_code='a') # lang_code must match voice
    generator = pipeline(lines, voice=TTSGeneration.VOICE, speed=TTSGeneration.SPEED)
    count = len(lines)
    for i, (_, _, audio) in enumerate(generator):
        print_progress_bar(i, count, "audio generated")
        clip_path = os.path.join(audio_dir, f'{i}.wav')
        sf.write(clip_path, audio, TTSGeneration.SAMPLE_RATE) # Save each audio file
    print_progress_bar(count, count, "audio generated\n")


if __name__ == "__main__":
    generate_tts()