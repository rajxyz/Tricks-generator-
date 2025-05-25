import json
import random
import logging
from fastapi import APIRouter, Query
from collections import defaultdict
from pathlib import Path
from enum import Enum

from .generate_template_sentence import (
    generate_template_sentence,
    load_templates as load_template_sentences,
    load_wordbank
)

from .generate_fixed_lines_sentence import generate_fixed_lines_sentence

router = APIRouter()
logger = logging.getLogger(__name__)
entity_index = defaultdict(int)

BASE_DIR = Path(__file__).resolve().parent.parent

# Default lines if no match is found
default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

# Trick types
class TrickType(str, Enum):
    actors = "actors"
    cricketers = "cricketers"
    animals = "animals"
    abbreviations = "abbreviations"
    simple_sentence = "simple_sentence"
    professions = "professions"  # NEW CATEGORY

# Mapping of template and data files
TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json",
    "simple_sentence": "English-templates.json",
    "professions": "Profession-templates.json"
}

DATA_FILE_MAP = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json",
    "abbreviations": "data.json",
    "simple_sentence": "wordbank.json",
    "professions": "professions.json"
}

# Wordbank cache for sentence generation
wordbank_cache = None

# Load entity data
def load_entities(trick_type, letter=None):
    filename = DATA_FILE_MAP.get(trick_type.lower())
    if not filename:
        logger.warning(f"No data file mapped for trick type: {trick_type}")
        return []

    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.warning(f"Entity data file not found: {file_path}")
        return []

    with file_path.open("r", encoding="utf-8") as f:
        entities = json.load(f)

    if letter and trick_type != "abbreviations":
        entities = [e for e in entities if e.get("name", "").upper().startswith(letter.upper())]

    logger.debug(f"Loaded {len(entities)} entities for type '{trick_type}' with letter '{letter}'")
    return entities

# Load wordbank for simple_sentence
def load_wordbank_file():
    file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
    if not file_path.exists():
        logger.warning(f"Wordbank file not found: {file_path}")
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

# Get next entity based on letter
def get_next_entities(trick_type, letters):
    selected = []
    for letter in letters:
        entities = load_entities(trick_type, letter[0])
        if entities:
            index = entity_index[(trick_type, letter)] % len(entities)
            selected.append(entities[index])
            entity_index[(trick_type, letter)] += 1
        else:
            logger.warning(f"No entities found for type '{trick_type}' and letter '{letter}'")
    return selected

# Logic for actor/cricketer/animal/profession style tricks
def handle_entity_based_trick(type, input_parts):
    template_file = TEMPLATE_FILE_MAP.get(type)
    templates = load_template_sentences(template_file)

    if all(len(w) == 1 for w in input_parts):
        entities = get_next_entities(type, input_parts)
        return generate_trick_sentence(entities, templates)
    else:
        topic = input_parts[0]
        rest_letters = [w[0].upper() for w in input_parts[1:] if w]
        entities = get_next_entities(type, rest_letters)
        return generate_trick_with_topic(topic, entities, templates)

# Generate sentence from templates for entity types
def generate_trick_sentence(entities, templates):
    if not entities:
        logger
