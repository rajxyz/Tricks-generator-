import json
import random
import logging
import re
from fastapi import APIRouter, Query
from pathlib import Path
from enum import Enum

from .generate_template_sentence import (
    generate_template_sentence,
    load_templates as load_template_sentences,
)

from wiki_utils import fetch_abbreviation_details
from cache import save_to_cache

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

class TrickType(str, Enum):
    abbreviations = "abbreviations"
    simple_sentence = "simple_sentence"

default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

DATA_FILE_MAP = {
    "abbreviations": "data.json",
    "simple_sentence": "wordbank.json"
}

TEMPLATE_FILE_MAP = {
    "simple_sentence": "English_templates.json"
}

wordbank_cache = None

def load_entities_abbr():
    file_path = BASE_DIR / DATA_FILE_MAP["abbreviations"]
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_wordbank():
    file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
    if not file_path.exists():
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def extract_letters(input_str):
    if "," in input_str:
        parts = [p.strip() for p in input_str.split(",") if p.strip()]
    else:
        if re.match(r"^[a-zA-Z]+$", input_str.strip()):
            parts = list(input_str.strip())
        else:
            parts = [w.strip() for w in re.findall(r'\\b\\w+\\b', input_str)]
    return parts

@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(..., description="Type of trick"),
    letters: str = Query(..., description="Comma-separated letters or words")
):
    global wordbank_cache
    input_parts = extract_letters(letters)

    if not input_parts:
        return {"trick": "Invalid input."}

    if type == TrickType.abbreviations:
        query = ''.join(input_parts).lower()
        data = load_entities_abbr()
        matched = [item for item in data if item.get("abbr", "").lower() == query]

        if matched:
            item = matched[0]
            return {
                "trick": f"{item['abbr']} — {item['full_form']}: {item['description']}"
            }

        wiki_data = fetch_abbreviation_details(query)

        if wordbank_cache is None:
            wordbank_cache = load_wordbank()

        built_words = []
        for i, letter in enumerate(input_parts):
            letter = letter.upper()
            possible_words = []

            for category in ['nouns', 'adjectives']:
                if letter in wordbank_cache.get(category, {}):
                    possible_words += wordbank_cache[category][letter]

            built_word = random.choice(possible_words).capitalize() if possible_words else letter
            built_words.append(built_word)

        built_full_form = " ".join(built_words)

        trick_output = f"{query.upper()} — {built_full_form}"
        if wiki_data["full_form"] != "Not found":
            trick_output += f": {wiki_data['description']}"
        else:
            trick_output += ": Description not available."

        save_to_cache({
            "abbr": query.upper(),
            "full_form": built_full_form,
            "description": wiki_data.get("description", "No description.")
        })

        return {"trick": trick_output}

    elif type == TrickType.simple_sentence:
        if wordbank_cache is None:
            wordbank_cache = load_wordbank()

        templates = load_template_sentences(TEMPLATE_FILE_MAP["simple_sentence"])
        if not templates:
            return {"trick": "No templates found."}

        template = random.choice(templates)

        sentence = generate_template_sentence(
            template,
            wordbank_cache,
            [l.upper() for l in input_parts]
        )

        return {"trick": sentence}

    return {"trick": "Invalid trick type selected."}
