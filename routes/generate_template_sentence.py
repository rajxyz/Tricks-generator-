import re
import random
from typing import List
import inflect
import json
from pathlib import Path

p = inflect.engine()

# Correct base dir to point to project root
BASE_DIR = Path(__file__).resolve().parent

def load_wordbank(filename="wordbank.json") -> dict:
    path = BASE_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_templates(filename="English-templates.json") -> List[str]:
    path = BASE_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("TEMPLATES", [])

def generate_template_sentence(template: str, wordbank: dict, input_letters: List[str]) -> str:
    placeholders = re.findall(r'([a-z_]+)', template.lower())
    
    for ph in placeholders:
        plural = False
        key = ph

        if key.endswith('_plural'):
            plural = True
            key = key[:-7]
        elif template.lower().find(f'[{ph}]s') != -1:
            plural = True

        json_key = key.capitalize() + 's' if key in ['noun', 'verb', 'adjective', 'adverb'] else key

        word_list = []
        for letter in input_letters:
            letter = letter.upper()
            word_list.extend(wordbank.get(json_key, {}).get(letter, []))

        if word_list:
            replacement = random.choice(word_list)
            if plural:
                replacement = p.plural(replacement)
        else:
            replacement = f"<{ph}>"

        if plural and template.lower().find(f'[{ph}]s') != -1:
            template = re.sub(rf'{ph}s', replacement, template, 1)
        else:
            template = template.replace(f'[{ph}]', replacement, 1)

    return template


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_template_sentence.py l t m")
        sys.exit(1)

    input_letters = sys.argv[1:]
    wordbank = load_wordbank()
    templates = load_templates()

    chosen_template = random.choice(templates)
    sentence = generate_template_sentence(chosen_template, wordbank, input_letters)

    print(sentence)
