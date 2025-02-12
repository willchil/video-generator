import os
from settings import ScriptAnnotation, SOURCE_DIRECTORY
from utility import approximate_duration, get_audio_clips


def divide_into_segments(durations, target):
    """
    Group sentences into subtitle segments so that each segment's total duration 
    is as close as possible to a fixed target duration, and return the list of indices
    where each segment begins.

    Parameters:
        durations (List[float]): List of caption durations (in seconds).
        target (float): The target duration for each subtitle (in seconds).
    
    Returns:
        List[int]: A list of indices indicating where each segment begins.
                   For example, if the segmentation is [[0, 1], [2], [3, 4]],
                   the function returns [0, 2, 3].
    
    Example:
        durations = [3.5, 2.0, 4.0, 1.5, 3.0]
        target = 5.0
        start_indices = divide_into_segments(durations, target)
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


def annotate_script(filename: str = 'script'):

    # Parse and split the caption file
    story_path = os.path.join(SOURCE_DIRECTORY, 'captions.txt')
    with open(story_path, 'r', encoding='utf-8') as f:
        text = f.read()
    captions = text.split("\n")
    captions = [line.strip() for line in captions if line.strip()]

    # Procedurally assigned image markers
    total_images = 0
    audio_clips = get_audio_clips(len(captions))
    durations = [audio_clips[i].duration if audio_clips[i] else approximate_duration(line) for i, line in enumerate(captions)]
    segment_indices = divide_into_segments(durations, ScriptAnnotation.TARGET_DURATION)
    for index in range(len(captions)):
        formatted = captions[index]
        if index in segment_indices:
            formatted = f"[{total_images}.png] {formatted}"
            total_images += 1
        captions[index] = formatted

    # Write the sentences to a new file, each on a new line
    file_path = os.path.join(SOURCE_DIRECTORY, f'{filename}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in captions:
            f.write(line + '\n\n')


if __name__ == "__main__":
    annotate_script("script")