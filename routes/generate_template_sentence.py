import random
import re
import json

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_template_sentence(template, grammar_helpers, wordbank, input_parts):
    """
    template: string with placeholders like [verb], [article], etc.
    grammar_helpers: dict with fixed word types (e.g. articles, prepositions)
    wordbank: dict with variable word types (e.g. nouns, verbs, adjectives)
    input_parts: list or set of word types expected in the sentence

    Returns a sentence with placeholders replaced by random words.
    """
    # Find all placeholders in the template
    placeholders = re.findall(r'(\w+)', template)

    for ph in placeholders:
        replacement = None

        # Replace only if in input_parts (optional, depending on your use case)
        if ph not in input_parts:
            continue

        # Try to get replacement from grammar_helpers first (fixed words)
        if ph in grammar_helpers and grammar_helpers[ph]:
            replacement = random.choice(grammar_helpers[ph])
        # Else try wordbank (variable words)
        elif ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])
        
        # If no word found, put placeholder tags for debug
        if replacement is None:
            replacement = f"<{ph}>"

        # Replace all occurrences of this placeholder
        template = template.replace(f'[{ph}]', replacement)

    return template
