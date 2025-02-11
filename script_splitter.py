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
                if current_line.strip(): lines.append(current_line.strip())
                current_line = sentence
            else:
                current_line += f'{sentence_seperator}{sentence}'

        lines.append(current_line.strip())
        script.extend(lines)

    # Procedurally assigned image markers
    total_images = 0
    durations = [approximate_duration(line) for line in script]
    segment_indices = divide_into_segments(durations, ScriptSplitter.TARGET_DURATION)
    for index in range(len(script)):
        formatted = script[index]
        if index in segment_indices:
            formatted = f"[{total_images}.png] {formatted}"
            total_images += 1
        script[index] = formatted

    return script


def divide_into_segments(durations, target):
    """
    Group sentences into subtitle segments so that each segment's total duration 
    is as close as possible to a fixed target duration, and return the list of indices
    where each segment begins.

    Parameters:
        durations (List[float]): List of sentence durations (in seconds).
        target (float): The target duration for each subtitle (in seconds).
    
    Returns:
        List[int]: A list of indices indicating where each segment begins.
                   For example, if the segmentation is [[0, 1], [2], [3, 4]],
                   the function returns [0, 2, 3].
    
    Example:
        durations = [3.5, 2.0, 4.0, 1.5, 3.0]
        target = 5.0
        start_indices = group_sentences_start_indices(durations, target)
        # One possible output is: [0, 2, 3]
    """
    n = len(durations)
    if n == 0:
        return []
    
    # Compute cumulative sums for O(1) range sum queries.
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + durations[i]

    # dp[i] will hold the minimum total cost for segmenting durations[0:i]
    dp = [float('inf')] * (n + 1)
    dp[0] = 0  # no sentences -> no cost

    # prev[i] will store the index where the last segment started for an optimal segmentation of durations[0:i]
    prev = [0] * (n + 1)

    # Fill in dp and prev using dynamic programming.
    for i in range(1, n + 1):
        # Try every possible start j for the final segment ending at i-1.
        for j in range(i):
            seg_duration = prefix[i] - prefix[j]
            cost = abs(seg_duration - target)
            if dp[j] + cost < dp[i]:
                dp[i] = dp[j] + cost
                prev[i] = j

    # Reconstruct the segmentation to obtain the starting indices.
    start_indices = []
    i = n
    while i > 0:
        j = prev[i]
        start_indices.append(j)
        i = j

    start_indices.reverse()
    return start_indices


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