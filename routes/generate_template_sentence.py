import random
import re
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Enable CORS
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
def generate_template_sentence(template: str, grammar_helpers: dict, wordbank: dict, input_letters: List[str]) -> str:
    placeholders = re.findall(r'([a-z_]+)', template)

    for ph in placeholders:
        replacement = None
        key = ph.lower()

        # Use grammar helpers if applicable
        if key in grammar_helpers and grammar_helpers[key]:
            replacement = random.choice(grammar_helpers[key])

        # Use wordbank if applicable (check by part of speech and letter)
        elif key in wordbank:
            word_list = []
            for letter in input_letters:
                word_list.extend(wordbank[key].get(letter.upper(), []))
            if word_list:
                replacement = random.choice(word_list)

        if not replacement:
            replacement = f"<{ph}>"

        template = template.replace(f'[{ph}]', replacement, 1)

    return template

# API route
@app.get("/api/tricks")
def get_tricks(type: str = "english_template_sentences", letters: str = ""):
    try:
        input_letters = letters.lower().split(",") if letters else []

        # Load data
        templates_data = load_json_file("data/templates.json")
        grammar_helpers = load_json_file("data/grammerhelpers.json")
        wordbank_raw = load_json_file("data/wordbank.json")

        # Normalize wordbank to structure by parts of speech and letter
        wordbank = {
            "noun": wordbank_raw.get("Nouns", {}),
            "verb": wordbank_raw.get("Verbs", {}),
            "adjective": wordbank_raw.get("Adjectives", {}),
            "adverb": wordbank_raw.get("Adverbs", {})
        }

        templates = templates_data.get(type, [])
        if not templates:
            return {"error": f"No templates found for type '{type}'"}

        template = random.choice(templates)
        trick = generate_template_sentence(template, grammar_helpers, wordbank, input_letters)

        return {"result": trick}

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}
