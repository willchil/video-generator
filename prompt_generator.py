import os
import requests
import socket
import subprocess
from settings import PromptGeneration, SOURCE_DIRECTORY
from utility import parse_lines, print_progress_bar


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

    if PromptGeneration.USE_OLLAMA:
        url = f'http://{PromptGeneration.HOST}:{PromptGeneration.PORT}/api/generate'
        data = {
            "model": PromptGeneration.MODEL,
            "prompt": text_prompt,
            "stream": False,
            "options": {
                "num_ctx": 16384
            }
        }
        response = requests.post(url, json=data)
        result = response.json()['response']

    else: # OpenAI chat completions API
        secure = PromptGeneration.PORT in [443, None]
        url = f"{f'https' if secure else 'http'}://{PromptGeneration.HOST}{'' if secure else f':{PromptGeneration.PORT}'}/v1/chat/completions"
        headers = { 
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PromptGeneration.API_KEY}" if PromptGeneration.API_KEY else ""
        }
        history = [{"role": "user", "content": text_prompt}]
        data = {
            "model": PromptGeneration.MODEL,
            "messages": history,
            "max_tokens": 2048
        }
        response = requests.post(url, headers=headers, json=data, verify=False)
        result = response.json()['choices'][0]['message']['content']

    # Filter out CoT in reasoning models
    think = "</think>"
    think_index = result.find(think)
    result = result if think_index == -1 else result[think_index + len(think):]

    return result.replace("\n", " ").strip()


def unload_ollama_model():
    def is_localhost(hostname):
        return hostname in ['localhost', '127.0.0.1', '::1'] or socket.gethostbyname(hostname) in ['127.0.0.1', '::1']
    if not PromptGeneration.USE_OLLAMA or not is_localhost(PromptGeneration.HOST): return
    subprocess.run(['ollama', 'stop', PromptGeneration.MODEL], check = True)


def generate_scenes(filename: str = "scenes"):
    lines = get_image_segments()

    with open('scene_template.txt', 'r', encoding='utf-8') as file:
        scene_template = file.read()

    prompts = ''
    path = os.path.join(SOURCE_DIRECTORY, f'{filename}.txt')
    for index, _ in enumerate(lines):
        print_progress_bar(index, len(lines), 'scenes generated')
        text_prompt = get_text_prompt(index, scene_template, lines)
        scene_description = get_response(text_prompt)
        prompts += '\n\n' + scene_description
        with open(path, 'w', encoding='utf-8') as f:
            f.write(prompts)
    print_progress_bar(len(lines), len(lines), 'scenes generated\n')

    # Write the final sentences to a new file, each on a new line
    prompts = prompts[2:] # Remove leading newline
    with open(path, 'w', encoding='utf-8') as f:
        f.write(prompts)


if __name__ == "__main__":
    generate_scenes("scenes")