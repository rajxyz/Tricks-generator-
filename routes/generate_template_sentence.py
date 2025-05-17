import random
import re
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path

app = FastAPI()

# Enable CORS for all origins (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to load a JSON file
def load_json_file(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Sentence generation with placeholder substitution
def generate_template_sentence(template: str, grammar_helpers: dict, wordbank: dict, input_parts: List[str]) -> str:
    # Correct regex to find placeholders like [noun], [verb], [adjective], etc.
    placeholders = re.findall(r'([a-z_]+)', template)

    for ph in placeholders:
        replacement = None

        # Try to get replacement from grammar helpers first
        if ph in grammar_helpers and grammar_helpers[ph]:
            replacement = random.choice(grammar_helpers[ph])
        # Then try from wordbank
        elif ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])

        # If no replacement found, show placeholder as unresolved
        if replacement is None:
            replacement = f"<{ph}>"

        # Replace only the first occurrence of this placeholder in the template
        template = template.replace(f'[{ph}]', replacement, 1)

    return template

@app.get("/api/tricks")
def get_tricks(type: str = "english_template_sentences", letters: str = ""):
    try:
        input_parts = letters.lower().split(",") if letters else []

        # Adjust these paths if your JSON files are elsewhere
        base_path = Path(__file__).parent / "data"
        templates_path = base_path / "templates.json"
        grammar_helpers_path = base_path / "grammar_helpers.json"
        wordbank_path = base_path / "wordbank.json"

        # Load JSON files
        templates_data = load_json_file(str(templates_path))
        grammar_helpers_raw = load_json_file(str(grammar_helpers_path))
        wordbank_raw = load_json_file(str(wordbank_path))

        # Normalize grammar helpers keys to lowercase
        grammar_helpers = {k.lower(): v for k, v in grammar_helpers_raw.items()}

        # Build wordbank dict with filtered words based on input letters for each category
        wordbank = {}
        for key in wordbank_raw:
            words = []
            for letter in input_parts:
                letter = letter.upper()
                if letter in wordbank_raw[key]:
                    words.extend(wordbank_raw[key][letter])
            wordbank[key.lower()] = words

        # Get list of templates for this type
        templates = templates_data.get(type, [])
        if not templates:
            return {"error": f"No templates found for type '{type}'"}

        # Pick a random template and generate the sentence
        template = random.choice(templates)
        trick = generate_template_sentence(template, grammar_helpers, wordbank, input_parts)

        return {"result": trick}

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}
