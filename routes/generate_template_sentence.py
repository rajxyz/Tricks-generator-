import random
import re

def generate_template_sentence(wordbank, templates, input_parts):
    # Choose a random template string from the templates list
    template = random.choice(templates)  # e.g. "[article] [adjective] [noun] [verb]s."

    # Find all placeholders in the template (e.g. article, adjective, noun, verb)
    placeholders = re.findall(r'(\w+)', template)

    # For each placeholder, pick a random word from the corresponding wordbank list
    for placeholder in placeholders:
        if placeholder in wordbank and wordbank[placeholder]:
            word = random.choice(wordbank[placeholder])
            # Replace the placeholder with the selected word
            template = template.replace(f'[{placeholder}]', word, 1)
        else:
            # If no word available, just replace with empty string
            template = template.replace(f'[{placeholder}]', '', 1)

    return template
