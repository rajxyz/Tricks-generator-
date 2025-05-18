import re
import random
from typing import List
import inflect

p = inflect.engine()

def generate_template_sentence(template: str, wordbank: dict, input_letters: List[str]) -> str:
    # Find placeholders like [noun], [verb], etc.
    placeholders = re.findall(r'([a-z_]+)', template.lower())

    for ph in placeholders:
        plural = False
        key = ph

        # Detect plural placeholder with '_plural' suffix or trailing 's'
        if key.endswith('_plural'):
            plural = True
            key = key[:-7]  # remove '_plural'
        elif template.lower().find(f'[{ph}]s') != -1:
            plural = True

        replacement = None
        # Your JSON keys have capitalized keys like "Nouns", "Verbs"
        json_key = key.capitalize() + 's' if key in ['noun', 'verb', 'adjective', 'adverb'] else key

        word_list = []
        for letter in input_letters:
            letter = letter.upper()
            word_list.extend(wordbank.get(json_key, {}).get(letter, []))

        if word_list:
            replacement = random.choice(word_list)
            if plural:
                replacement = p.plural(replacement)

        if not replacement:
            replacement = f"<{ph}>"

        # Replace with or without trailing 's'
        if plural and template.lower().find(f'[{ph}]s') != -1:
            template = re.sub(rf'{ph}s', replacement, template, 1)
        else:
            template = template.replace(f'[{ph}]', replacement, 1)

    return template
