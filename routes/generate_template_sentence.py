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
    placeholders = re.findall(r'(\w+)', template)

    for ph in placeholders:
        plural = False
        base_ph = ph

        # Handle plural markers like "nouns", "verbs"
        if base_ph.endswith('s') and base_ph[:-1] in ['noun', 'verb', 'adjective', 'adverb']:
            plural = True
            base_ph = base_ph[:-1]

        # Determine the wordbank key
        json_key = base_ph.capitalize() + 's' if base_ph in ['noun', 'verb', 'adjective', 'adverb'] else base_ph

        # Collect word list based on input letters
        word_list = []
        for letter in input_letters:
            word_list.extend(wordbank.get(json_key, {}).get(letter.upper(), []))

        # Fallback placeholder if no word found
        if word_list:
            word = random.choice(word_list)
            if plural:
                word = p.plural(word)
        else:
            word = f"<{ph}>"

        # Replace one occurrence at a time
        template = template.replace(f"[{ph}]", word, 1)

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
