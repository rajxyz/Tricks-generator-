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

    # Find all placeholders like [verb], [adverb]
    placeholders = re.findall(r'(\w+)', template)

    # For each placeholder, replace it with a random word from wordbank if available
    for ph in placeholders:
        # Only replace placeholders present in input_parts and wordbank
        if ph in input_parts and ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])
        else:
            # If no suitable replacement, keep placeholder or replace with empty string
            replacement = f"<{ph}>"  # or "" if you prefer
        # Replace all occurrences of this placeholder in template
        template = template.replace(f'[{ph}]', replacement)

    return template
