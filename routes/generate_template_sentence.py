import random
import re
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_template_sentence(template: str, grammar_helpers: dict, wordbank: dict, input_parts: List[str]):
    placeholders = re.findall(r'([a-z_]+)', template)

    for ph in placeholders:
        replacement = None
        if ph not in input_parts:
            continue

        if ph in grammar_helpers and grammar_helpers[ph]:
            replacement = random.choice(grammar_helpers[ph])
        elif ph in wordbank and wordbank[ph]:
            replacement = random.choice(wordbank[ph])

        if replacement is None:
            replacement = f"<{ph}>"

        template = template.replace(f'[{ph}]', replacement, 1)

    return template

@app.get("/api/tricks")
def get_tricks(type: str = "english_template_sentences", letters: str = ""):
    try:
        input_parts = letters.lower().split(",") if letters else []

        # Load files
        templates_data = load_json_file("data/templates.json")
        grammar_helpers = load_json_file("data/grammar_helpers.json")
        grammar_helpers = {k.lower(): v for k, v in grammar_helpers.items()}

        raw_wordbank = load_json_file("data/wordbank.json")
        selected_nouns = []
        if "Nouns" in raw_wordbank:
            for letter in input_parts:
                nouns = raw_wordbank["Nouns"].get(letter.upper(), [])
                selected_nouns.extend(nouns)

        wordbank = {
            "noun": selected_nouns
        }

        templates = templates_data.get(type, [])
        if not templates:
            return {"error": f"No templates found for type '{type}'"}

        template = random.choice(templates)
        trick = generate_template_sentence(template, grammar_helpers, wordbank, input_parts)

        return {"result": trick}
    except Exception as e:
        return {"error": str(e)}
