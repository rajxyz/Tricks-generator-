import json
import random
import logging
import re
from fastapi import APIRouter, Query
from pathlib import Path
from enum import Enum

from .generate_template_sentence import generate_template_sentence, load_templates

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

class TrickType(str, Enum):
    animals = "animals"
    actors = "actors"
    cricketers = "cricketers"

DATA_FILES = {
    "animals": "data/animals.json",
    "actors": "data/actors.json",
    "cricketers": "data/cricketers.json"
}

TEMPLATE_FILES = {
    "animals": "data/templates/animal_templates.json",
    "actors": "data/templates/actor_templates.json",
    "cricketers": "data/templates/cricketer_templates.json"
}

def extract_letters_or_words(input_str):
    if "," in input_str:
        parts = [p.strip() for p in input_str.split(",") if p.strip()]
    elif re.match(r"^[a-zA-Z]+$", input_str.strip()):
        parts = list(input_str.strip())
    else:
        parts = [w.strip() for w in re.findall(r'\b\w+\b', input_str)]
    return parts

def load_json_file(path):
    full_path = BASE_DIR / path
    if not full_path.exists():
        logger.warning(f"File not found: {full_path}")
        return []
    with full_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def find_matching_entry(letter, data, use_surname=False):
    matches = []
    for item in data:
        name = item.get("name", "")
        surname = item.get("surname", "")
        target = surname if use_surname else name
        if target and target[0].lower() == letter.lower():
            full_name = f"{name} {surname}".strip()
            matches.append(full_name)
    return random.choice(matches) if matches else letter.upper()

@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(...),
    letters: str = Query(...)
):
    logger.info(f"[API] Type: {type}, Letters: {letters}")
    input_parts = extract_letters_or_words(letters)
    logger.debug(f"[API] Normalized input: {input_parts}")

    if not input_parts:
        return {"trick": "Invalid input."}

    templates = load_templates(str(BASE_DIR / TEMPLATE_FILES[type]))
    if not templates:
        return {"trick": "No templates available."}

    selected_template = random.choice(templates)
    logger.debug(f"[TEMPLATE] Selected: {selected_template}")

    data = load_json_file(DATA_FILES[type])

    final_words = []
    for i, letter in enumerate(input_parts):
        is_last = (i == len(input_parts) - 1)

        if type == TrickType.actors:
            # Use full name on last, first name otherwise
            name = find_matching_entry(letter, data, use_surname=False if not is_last else False)
        elif type == TrickType.cricketers:
            # Use surname on last, first name otherwise
            name = find_matching_entry(letter, data, use_surname=is_last)
        else:
            # Animals or generic
            name = find_matching_entry(letter, data)

        final_words.append(name)

    trick_line = selected_template.replace("{words}", ", ".join(final_words))
    logger.info(f"[TRICK] Output: {trick_line}")

    return {"trick": trick_line}
    
