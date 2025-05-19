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
    print("\n--- DEBUGGING TEMPLATE GENERATION ---")
    print(f"Original template: {template}")
    print(f"Input letters: {input_letters}")

    # Corrected regex to match [placeholder] format
    placeholders = re.findall(r'([a-z_]+)', template.lower())
    print(f"Detected placeholders: {placeholders}")

    for ph in placeholders:
        plural = False
        base_ph = ph

        if base_ph.endswith('s') and base_ph[:-1] in ['noun', 'verb', 'adjective', 'adverb']:
            plural = True
            base_ph = base_ph[:-1]

        json_key = base_ph.capitalize() + 's' if base_ph in ['noun', 'verb', 'adjective', 'adverb'] else base_ph

        print(f"\nHandling placeholder: {ph}")
        print(f"Base placeholder: {base_ph}")
        print(f"Plural: {plural}")
        print(f"Looking in wordbank key: {json_key}")

        word_list = []
        for letter in input_letters:
            upper_letter = letter.upper()
            matched = wordbank.get(json_key, {}).get(upper_letter, [])
            print(f"  Letter '{upper_letter}' => {matched}")
            word_list.extend(matched)

        if word_list:
            word = random.choice(word_list)
            if plural:
                word = p.plural(word)
            print(f"Chosen word: {word}")
        else:
            word = f"<{ph}>"
            print(f"No match found, using placeholder: {word}")

        # Use regex to safely replace one placeholder occurrence at a time
        template = re.sub(rf'{ph}', word, template, count=1)

    print(f"Final sentence: {template}")
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
    print(f"\nChosen Template: {chosen_template}")
    sentence = generate_template_sentence(chosen_template, wordbank, input_letters)

    print(f"\nGenerated Sentence: {sentence}")
