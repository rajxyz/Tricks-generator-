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
    # Fix placeholder regex
    placeholders = re.findall(r'(\w+)', template)

    for ph in placeholders:
        replacement = None

        # Replace only if in input_parts
        if ph not in input_parts:
            continue

        # First check fixed word types (grammar_helpers)
        if ph in grammar_helpers and grammar_helpers[ph]:
            replacement = random.choice(grammar_helpers[ph])
        # Then check wordbank (variable types)
        elif ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])
        
        # If nothing found
        if replacement is None:
            replacement = f"<{ph}>"

        # Replace all occurrences of this placeholder
        template = template.replace(f'[{ph}]', replacement)

    return template
