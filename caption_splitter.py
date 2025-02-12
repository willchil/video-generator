import nltk
import os
from settings import CaptionSplitter, SOURCE_DIRECTORY
from typing import List


def split_lines(text: str, max_characters: int) -> List[str]:

    paragraphs = text.split("\n")
    paragraphs = [line.strip() for line in paragraphs if line.strip()]

    captions: List[str] = []
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
        captions.extend(lines)

    return captions


def split_captions(filename: str = 'captions'):

    # Parse and split the provided story file
    story_path = os.path.join(SOURCE_DIRECTORY, 'story.txt')
    with open(story_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = split_lines(text, CaptionSplitter.MAX_CHARACTERS)

    # Write the sentences to a new file, each on a new line
    file_path = os.path.join(SOURCE_DIRECTORY, f'{filename}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n\n')


if __name__ == "__main__":
    split_captions("captions")