import re
import random
from typing import List
import inflect

p = inflect.engine()

def generate_template_sentence(template: str, wordbank: dict, input_letters: List[str]) -> str:
    # Find all placeholders like [noun], [verb], [adjective], etc.
    placeholders = re.findall(r'([a-z_]+)', template.lower())

    for ph in placeholders:
        plural = False
        base_ph = ph

        # Detect plural
        if base_ph.endswith('_plural'):
            plural = True
            base_ph = base_ph[:-7]
        elif f"[{ph}]s" in template:
            plural = True

        # Match to wordbank keys
        json_key = base_ph.capitalize() + 's' if base_ph in ['noun', 'verb', 'adjective', 'adverb'] else base_ph.capitalize()

        # Gather matching words
        word_list = []
        for letter in input_letters:
            letter = letter.upper()
            word_list.extend(wordbank.get(json_key, {}).get(letter, []))

        replacement = random.choice(word_list) if word_list else f"<{base_ph}>"
        if plural:
            replacement = p.plural(replacement)

        # Replace placeholders
        if plural and f"[{ph}]s" in template:
            template = re.sub(rf'{ph}s', replacement, template, count=1)
        else:
            template = re.sub(rf'{ph}', replacement, template, count=1)

    return template
