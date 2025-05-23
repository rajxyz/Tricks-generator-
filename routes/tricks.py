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

router = APIRouter()
logger = logging.getLogger(__name__)
entity_index = defaultdict(int)

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
    abbreviations = "abbreviations"
    simple_sentence = "simple_sentence"
    professions = "professions"  # added new

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

def load_entities(trick_type, letter=None):
    try:
        filename = DATA_FILE_MAP.get(trick_type.lower())
        if not filename:
            logger.error(f"No data file for trick_type: {trick_type}")
            return []

        file_path = BASE_DIR / filename
        if not file_path.exists():
            logger.error(f"Entity data file not found: {file_path}")
            return []

        with file_path.open("r", encoding="utf-8") as f:
            entities = json.load(f)

        if letter and trick_type != "abbreviations":
            entities = [e for e in entities if e.get("name", "").upper().startswith(letter.upper())]

        logger.debug(f"Loaded {len(entities)} entities for '{trick_type}' with letter '{letter}'")
        logger.debug(f"Sample entity names: {[e.get('name') for e in entities[:5]]}")
        return entities

    except Exception as e:
        logger.exception(f"Error loading entities for {trick_type} with letter {letter}: {e}")
        return []
