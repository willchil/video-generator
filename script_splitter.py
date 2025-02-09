import numpy as np
import nltk
import os
from render_clips import approximate_duration
from settings import ScriptSplitter, SOURCE_DIRECTORY
from typing import List


def split_lines(text: str, max_characters: int) -> List[str]:

    paragraphs = text.split("\n")
    paragraphs = [line.strip() for line in paragraphs if line.strip()]

    script: List[str] = []
    nltk.download('punkt_tab')
    sentence_seperator = ' '

    for paragraph in paragraphs:

        sentences = nltk.sent_tokenize(paragraph)
        lines: List[str] = []

        current_line = ""
        for sentence in sentences:
            if len(current_line) + len(sentence) + len(sentence_seperator) > max_characters:
                lines.append(current_line.strip())
                current_line = sentence
            else:
                current_line += f'{sentence_seperator}{sentence}'

        lines.append(current_line.strip())
        script.extend(lines)

    # Procedurally assigned image markers
    total_images = 0
    segment_indices = divide_into_segments(script, ScriptSplitter.TARGET_DURATION)
    for index in range(len(script)):
        formatted = script[index]
        if index in segment_indices:
            formatted = f"[{total_images}.png] {formatted}"
            total_images += 1
        script[index] = formatted

    return script


def divide_into_segments(lines, target):
    """
    Divides lines from the script out into groups for each image.

    Parameters:
    lines (List[str]): The lines from the script
    target (int): The target duration in seconds for each image
    """

    durations = [approximate_duration(line) for line in lines]

    # Initialize the cumulative sum and the list of indices
    cum_sum = np.cumsum(durations)
    indices = [0]

    # Iterate over the cumulative sum
    for i in range(len(cum_sum)):
        # If the current cumulative sum minus the sum of the previous segments is greater than the target
        if cum_sum[i] - cum_sum[indices[-1]] > target:
            # Add the index to the list of indices
            indices.append(i)

    # Return the list of indices
    return indices


def generate_script(filename: str = 'script'):
    # Test the function with the provided input string
    story_path = os.path.join(SOURCE_DIRECTORY, 'story.txt')
    with open(story_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = split_lines(text, ScriptSplitter.MAX_CHARACTERS)

    # Write the sentences to a new file, each on a new line
    file_path = os.path.join(SOURCE_DIRECTORY, f'{filename}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n\n')


if __name__ == "__main__":
    generate_script("script-temp")