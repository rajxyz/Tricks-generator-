import json
import random
import logging
import re
from fastapi import APIRouter, Query
from pathlib import Path

# ---- Setup ----
router = APIRouter()
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- Fallback lines ----
default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

# ---- Template Mapping by Length and Category ----
TEMPLATE_BY_LEN = {
    5: {
        "actor": "templates_actor_5.json",
        "animal": "templates_animal_5.json",
        "cricketer": "templates_cricketer_5.json"
    },
    6: {
        "actor": "templates_actor_6.json",
        "animal": "templates_animal_6.json",
        "cricketer": "templates_cricketer_6.json"
    },
    7: {
        "actor": "templates_actor_7.json",
        "animal": "templates_animal_7.json",
        "cricketer": "templates_cricketer_7.json"
    },
    8: {
        "actor": "templates_actor_8.json",
        "animal": "templates_animal_8.json",
        "cricketer": "templates_cricketer_8.json"
    },
    9: {
        "actor": "templates_actor_9.json",
        "animal": "templates_animal_9.json",
        "cricketer": "templates_cricketer_9.json"
    },
    10: {
        "actor": "templates_actor_10.json",
        "animal": "templates_animal_10.json",
        "cricketer": "templates_cricketer_10.json"
    }
}

# ---- Extract First Letters ----
def extract_letters(input_str):
    if "," in input_str:
        return [p.strip().upper() for p in input_str.split(",") if p.strip()]
    elif re.match(r"^[a-zA-Z]+$", input_str.strip()):
        return list(input_str.strip().upper())
    else:
        return [w[0].upper() for w in re.findall(r'\b\w+', input_str)]

# ---- Load Wordbank ----
def load_wordbank():
    path = BASE_DIR / "wordbank.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    else:
        logger.warning("[LOAD] wordbank.json not found!")
        return {}

# ---- Load Templates ----
def load_templates(filename):
    path = BASE_DIR / filename
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    else:
        logger.warning(f"[LOAD] Template file {filename} not found!")
        return []

# ---- Generate Sentence from Template ----
def generate_template_sentence(template, wordbank, letters):
    words = []
    for letter in letters:
        options = wordbank.get(letter.upper(), [])
        if options:
            word = random.choice(options)
            words.append(word)
        else:
            logger.debug(f"[GEN] No word found for letter '{letter}'")
            words.append(letter.upper())

    try:
        return template.format(*words)
    except Exception as e:
        logger.error(f"[GEN] Template formatting failed: {e}")
        return random.choice(default_lines)

# ---- FastAPI Route ----
wordbank_cache = None

@router.get("/api/tricks")
def get_tricks(
    letters: str = Query(..., description="Comma-separated letters or words"),
    category: str = Query("actor", pattern="^(actor|animal|cricketer)$")
):
    global wordbank_cache

    logger.info(f"[API] Letters received: {letters} | Category: {category}")
    input_parts = extract_letters(letters)
    input_length = len(input_parts)
    logger.debug(f"[API] Normalized letters: {input_parts} | Length: {input_length}")

    if not input_parts:
        return {"trick": "Invalid input."}

    if wordbank_cache is None:
        wordbank_cache = load_wordbank()
        logger.debug(f"[LOAD] Wordbank loaded with {len(wordbank_cache)} letters.")

    # Load category-specific template for length >= 5
    template_file = TEMPLATE_BY_LEN.get(input_length, {}).get(category)
    if template_file:
        templates = load_templates(template_file)
    else:
        templates = []

    if not templates:
        logger.warning("[API] No matching templates found. Using fallback message.")
        return {"trick": random.choice(default_lines)}

    selected_template = random.choice(templates)
    sentence = generate_template_sentence(selected_template, wordbank_cache, input_parts)

    logger.info(f"[API] Trick generated: {sentence}")
    return {"trick": sentence}
