import json
import random
import logging
import re
from fastapi import APIRouter, Query
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_LINES = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

CATEGORY_TEMPLATES = {
    "animals": "templates/animal_templates.json",
    "actors": "templates/actor_templates.json",
    "cricketers": "templates/cricketer_templates.json"
}

WORDBANK_FILE = BASE_DIR / "data" / "wordbank.json"

# Helper to extract clean letters or names from input
def extract_letters(input_str):
    if "," in input_str:
        parts = [p.strip() for p in input_str.split(",") if p.strip()]
    else:
        if re.match(r"^[a-zA-Z]+$", input_str.strip()):
            parts = list(input_str.strip())
        else:
            parts = [w.strip() for w in re.findall(r'\b\w+\b', input_str)]
    return parts

# Load templates from file
def load_templates(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"[TEMPLATE] Failed loading {file_path}: {e}")
        return []

# Load wordbank data
wordbank_cache = None
def load_wordbank():
    global wordbank_cache
    if wordbank_cache:
        return wordbank_cache
    try:
        with open(WORDBANK_FILE, encoding="utf-8") as f:
            wordbank_cache = json.load(f)
        return wordbank_cache
    except Exception as e:
        logger.warning(f"[WORDBANK] Load failed: {e}")
        return {}

# Core sentence generator
def generate_rhyming_sentence(category, letters):
    templates = load_templates(CATEGORY_TEMPLATES.get(category, ""))
    if not templates:
        return random.choice(DEFAULT_LINES)

    template = random.choice(templates)
    wordbank = load_wordbank()

    used_names = []
    last_index = len(letters) - 1

    for idx, l in enumerate(letters):
        l = l.upper()
        pick_name = None

        if category == "animals":
            pick_name = random.choice(wordbank.get("animals", {}).get(l, [l]))
        else:
            names = wordbank.get(category, {}).get(l, [])
            if not names:
                used_names.append(l)
                continue

            if idx < 3:  # Always pick first name only
                pick_name = random.choice([n.split()[0] for n in names])
            elif category == "actors":
                pick_name = random.choice([n.split()[0] for n in names])
            elif category == "cricketers":
                pick_name = random.choice(names)  # full name (name + surname)

        used_names.append(pick_name or l)

    sentence = template.replace("{names}", ", ".join(used_names))
    return sentence

@router.get("/api/tricks")
def get_trick(
    type: str = Query(..., description="Category of trick: animals, actors, cricketers"),
    letters: str = Query(..., description="Comma-separated letters or words")
):
    type = type.lower()
    logger.info(f"Request received: type={type}, letters={letters}")

    if type not in CATEGORY_TEMPLATES:
        return {"trick": "Invalid type provided."}

    parts = extract_letters(letters)
    logger.debug(f"Cleaned parts: {parts}")

    if not parts:
        return {"trick": "No valid input found."}

    if len(parts) < 4:
        return {"trick": random.choice(DEFAULT_LINES)}

    trick = generate_rhyming_sentence(type, parts[:4])
    return {"trick": trick}
        
