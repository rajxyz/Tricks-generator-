import random
import re

def generate_template_sentence(wordbank, templates, input_letters):
    if not input_letters or not templates:
        return "Invalid input."

    template = random.choice(templates)
    placeholders = re.findall(r"(.*?)", template)
    filled = {}

    for i, placeholder in enumerate(placeholders):
        letter_index = i % len(input_letters)
        letter = input_letters[letter_index].lower()
        words = wordbank.get(placeholder, [])
        matching = [w for w in words if w.lower().startswith(letter)]

        if matching:
            filled[placeholder] = random.choice(matching)
        else:
            filled[placeholder] = f"[{placeholder}]"

    for key, val in filled.items():
        template = template.replace(f"[{key}]", val, 1)

    return template
