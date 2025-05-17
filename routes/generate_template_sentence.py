import random
import re
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

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
    placeholders = re.findall(r'([a-z_]+)', template)

    for ph in placeholders:
        replacement = None

        # Only process placeholders that are among user’s selected parts
        if ph not in input_parts:
            continue

        # First try grammar_helpers (like prepositions etc.)
        if ph in grammar_helpers and grammar_helpers[ph]:
            replacement = random.choice(grammar_helpers[ph])

        # Then try wordbank (noun, verb, adjective, adverb — by letter)
        elif ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])

        if replacement is None:
            replacement = f"<{ph}>"

        template = template.replace(f'[{ph}]', replacement, 1)

    return template

# API route
@app.get("/api/tricks")
def get_tricks(type: str = "english_template_sentences", letters: str = ""):
    try:
        input_parts = letters.lower().split(",") if letters else []

        # Load data files
        templates_data = load_json_file("data/templates.json")
        grammar_helpers = load_json_file("data/grammarhelpers.json")
        wordbank_raw = load_json_file("data/wordbank.json")

        # Build filtered wordbank based on input letters
        wordbank = {
            "noun": [],
            "verb": [],
            "adjective": [],
            "adverb": []
        }

        for part in wordbank.keys():
            for letter in input_parts:
                entries = wordbank_raw.get(part.capitalize() + "s", {}).get(letter.upper(), [])
                wordbank[part].extend(entries)

        # Get templates
        templates = templates_data.get(type, [])
        if not templates:
            return {"error": f"No templates found for type '{type}'"}

        template = random.choice(templates)
        trick = generate_template_sentence(template, grammar_helpers, wordbank, input_parts)

        return {"result": trick}

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}
