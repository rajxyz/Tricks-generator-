import re
import random
from typing import List

def generate_template_sentence(template: str, wordbank: dict, input_letters: List[str]) -> str:
    # Find all placeholders like [noun], [verb], etc.
    placeholders = re.findall(r'([a-z_]+)', template.lower())

    for ph in placeholders:
        replacement = None
        key = ph.lower()

        # Handle parts of speech that are mapped by letter
        if key in ['noun', 'verb', 'adjective', 'adverb']:
            word_list = []
            for letter in input_letters:
                letter = letter.upper()
                word_list.extend(wordbank.get(key.capitalize() + 's', {}).get(letter, []))
            if word_list:
                replacement = random.choice(word_list)

        # Handle flat list word types (like prepositions, conjunctions, etc.)
        elif key in wordbank and isinstance(wordbank[key], list):
            replacement = random.choice(wordbank[key])

        # Fallback in case nothing found
        if not replacement:
            replacement = f"<{ph}>"

        template = template.replace(f'[{ph}]', replacement, 1)

    return template
