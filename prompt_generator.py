import os
import requests
import sys
from settings import PromptGeneration
from video import SOURCE_DIRECTORY, parse_lines


def get_image_segments():
    lines = [(line[1], line[2]) for line in parse_lines()]
    segments = []
    current_segment = ''
    for line in lines:
        if line[0] != None and current_segment:
            segments.append(current_segment.strip())
            current_segment = ''
        current_segment += line[1] + '\n'
    segments.append(current_segment)
    return segments


def get_text_prompt(line_index: int, template: str, lines) -> str:

   # Get the requested line and the lines before and after
   line = lines[line_index]
   before = '\n'.join(lines[:line_index])
   after = '\n'.join(lines[line_index+1:])

   # Replace placeholders in template
   formatted = template.replace('<LINE>', line)
   formatted = formatted.replace('<BEFORE>', before)
   formatted = formatted.replace('<AFTER>', after)

   return formatted


def get_response(text_prompt: str) -> str:
    url = f'http://{PromptGeneration.HOST}:{PromptGeneration.PORT}/v1/chat/completions'
    headers = { "Content-Type": "application/json" }
    history = [{"role": "user", "content": text_prompt}]
    data = {
        "model": PromptGeneration.MODEL,
        "messages": history,
        "max_tokens": 1024
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    result = response.json()['choices'][0]['message']['content']
    return result.replace("\n", " ").strip()

def print_progress_bar(index, total):
    n_bar = 50  # Progress bar width
    progress = index / total
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'=' * int(n_bar * progress):{n_bar}s}] {index} / {total} Scenes generated")
    sys.stdout.flush()


def generate_scenes(filename: str = "scenes"):
    lines = get_image_segments()

    with open('scene_template.txt', 'r', encoding='utf-8') as file:
        scene_template = file.read()

    prompts = ''
    path = os.path.join(SOURCE_DIRECTORY, f'{filename}.txt')
    for index, _ in enumerate(lines):
        print_progress_bar(index, len(lines))
        text_prompt = get_text_prompt(index, scene_template, lines)
        scene_description = get_response(text_prompt)
        prompts += '\n\n' + scene_description
        with open(path, 'w', encoding='utf-8') as f:
            f.write(prompts)
    print_progress_bar(len(lines), len(lines))

    # Write the final sentences to a new file, each on a new line
    prompts = prompts[2:] # Remove leading newline
    with open(path, 'w', encoding='utf-8') as f:
        f.write(prompts)

if __name__ == "__main__":
    generate_scenes("scenes-temp")