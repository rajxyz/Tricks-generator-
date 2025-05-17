import random
import re

def generate_template_sentence(wordbank, templates, input_parts):
    """
    wordbank: dict of word types to lists, e.g. {'verb': ['run', 'jump'], 'adverb': ['quickly']}
    templates: list of strings with placeholders like '[verb]', '[adverb]', etc.
    input_parts: list or set of word types you want to include in the sentence

    Returns a generated sentence by picking a random template and replacing placeholders.
    """
    if not templates:
        return "No templates available."

    # Pick a random template
    template = random.choice(templates)

    # Correct regex to find [placeholder] format
    placeholders = re.findall(r'(\w+)', template)

    # For each placeholder, replace it with a random word from wordbank if available
    for ph in placeholders:
        if ph in input_parts and ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])
        else:
            replacement = f"<{ph}>"
        template = template.replace(f'[{ph}]', replacement)

    return template
