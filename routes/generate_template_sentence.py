import random
import re

def generate_template_sentence(wordbank, templates, input_parts):
    """
    Generates a sentence by selecting a template and filling placeholders with words from the wordbank.

    Parameters:
    - wordbank: dict of word types to word lists (e.g. {'verb': ['run'], 'noun': ['dog']})
    - templates: list of sentence templates with placeholders like [verb], [noun]
    - input_parts: list or set of word types you want to include

    Returns:
    - A generated sentence with placeholders replaced.
    """
    if not templates:
        return "No templates available."

    # Pick a random template
    template = random.choice(templates)

    # Find all placeholders like [verb], [noun], etc.
    placeholders = re.findall(r'(\w+)', template)

    # Replace each placeholder
    for ph in placeholders:
        if ph in input_parts and ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])
        else:
            replacement = f"<{ph}>"  # fallback if no matching word
        template = template.replace(f'[{ph}]', replacement)

    return template


# --- Test Example (can be removed in production) ---
if __name__ == "__main__":
    wordbank = {
        "article": ["The", "A"],
        "adjective": ["quick", "lazy"],
        "noun": ["fox", "dog"],
        "verb": ["jump", "run"],
        "adverb": ["quickly", "silently"]
    }

    templates = [
        "[article] [adjective] [noun] [verb]s.",
        "[article] [noun] [adverb] [verb]s over the [adjective] [noun]."
    ]

    input_parts = {"article", "adjective", "noun", "verb", "adverb"}

    for _ in range(5):
        print(generate_template_sentence(wordbank, templates, input_parts))
