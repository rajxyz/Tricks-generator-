import json
import random
import logging
from fastapi import APIRouter, Query
from pathlib import Path
from enum import Enum

from .generate_template_sentence import (
    load_templates as load_template_sentences
)

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

class TrickType(str, Enum):
    actors = "actors"
    cricketers = "cricketers"
    animals = "animals"

TEMPLATE_FILE_MAP = {
    "actors": "actors_templates.json",
    "cricketers": "cricketers_templates.json",
    "animals": "animals_templates.json"
}

DATA_FILE_MAP = {
    "actors": "actors.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json"
}

def load_entities(category):
    path = BASE_DIR / DATA_FILE_MAP[category]
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_templates(category):
    path = BASE_DIR / TEMPLATE_FILE_MAP[category]
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_letters(input_str):
    if "," in input_str:
        return [w.strip() for w in input_str.split(",") if w.strip()]
    return list(input_str.strip())

def find_template_key(last_word, templates):
    key = last_word.lower()
    if key in templates:
        return key
    for k in templates:
        if key in k.lower():
            return k
    return None

def select_display_name(entity, is_last, category):
    name = entity.get("name", "")
    parts = name.strip().split()
    if not parts:
        return name

    if category == "animals":
        return name
    if is_last:
        if category == "actors":
            return name
        elif category == "cricketers":
            return parts[-1]
    return parts[0]

def generate_trick_sentence(entities, templates, category):
    if not entities:
        return "No data found for the entered letters."

    names = []
    for i, e in enumerate(entities):
        is_last = i == len(entities) - 1
        names.append(select_display_name(e, is_last, category))

    combined = ", ".join(names)
    last_key = names[-1].lower()

    match_key = find_template_key(last_key, templates)
    if match_key:
        line = random.choice(templates[match_key])
    else:
        line = random.choice(default_lines)

    return f"{combined}: {line}"

@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(..., description="Trick category"),
    letters: str = Query(..., description="Comma-separated words or letters")
):
    logger.info(f"Request received: type={type}, letters={letters}")
    input_parts = extract_letters(letters)
    logger.info(f"Extracted parts: {input_parts}")

    if not input_parts:
        return {"trick": "Invalid input."}

    all_entities = load_entities(type)
    templates = load_templates(type)

    matched_entities = []
    for letter in input_parts:
        for entity in all_entities:
            if entity.get("name", "").lower().startswith(letter.lower()):
                matched_entities.append(entity)
                break

    trick = generate_trick_sentence(matched_entities, templates, type)
    return {"trick": trick}
