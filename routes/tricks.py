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
    professions = "professions"

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

wordbank_cache = None

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

def load_wordbank_file():
    file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
    if not file_path.exists():
        logger.warning(f"Wordbank file not found: {file_path}")
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)

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

def handle_entity_based_trick(type, input_parts):
    template_file = TEMPLATE_FILE_MAP.get(type)
    templates = load_template_sentences(template_file)

    if all(len(w) == 1 for w in input_parts):
        entities = get_next_entities(type, input_parts)
        return generate_trick_sentence(entities, templates, type)
    else:
        topic = input_parts[0]
        rest_letters = [w[0].upper() for w in input_parts[1:] if w]
        entities = get_next_entities(type, rest_letters)
        return generate_trick_with_topic(topic, entities, templates, type)

def generate_trick_sentence(entities, templates, trick_type):
    if not entities:
        logger.warning("No entities provided to generate_trick_sentence.")
        return "No names found for the entered letters."

    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        logger.warning("Entities loaded but names are missing or malformed.")
        return "Entity names missing or malformed."

    selected_name = names[-1]
    key_map = {k.lower(): v for k, v in templates.items()}
    matched_line = key_map.get(selected_name.lower())

    if matched_line:
        logger.debug(f"[MATCH] Type: {trick_type} | Name: {selected_name}")
        line = random.choice(matched_line)
    else:
        logger.debug(f"[FALLBACK] Type: {trick_type} | Name: {selected_name} — using default.")
        line = random.choice(default_lines)

    return f"{', '.join(names)}: {line}"

def generate_trick_with_topic(topic, entities, templates, trick_type):
    if not entities:
        logger.warning(f"No entities found for topic-based trick with topic '{topic}'")
        return f"{topic}: {random.choice(default_lines)}"

    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        logger.warning(f"Entity names missing or malformed for topic '{topic}'")
        return f"{topic}: Entity names missing or malformed."

    selected_name = names[-1]
    key_map = {k.lower(): v for k, v in templates.items()}
    matched_line = key_map.get(selected_name.lower())

    if matched_line:
        logger.debug(f"[MATCH] Topic: {topic} | Type: {trick_type} | Name: {selected_name}")
        line = random.choice(matched_line)
    else:
        logger.debug(f"[FALLBACK] Topic: {topic} | Type: {trick_type} | Name: {selected_name} — using default.")
        line = random.choice(default_lines)

    return f"<b>{topic}</b>, {', '.join(names)}: {line}"

@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(TrickType.actors, description="Type of trick"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    global wordbank_cache

    input_parts = [w.strip() for w in letters.split(",")] if letters else []
    input_parts = [w for w in input_parts if w]

    logger.debug(f"Received type: {type}, input_parts: {input_parts}")

    if not input_parts:
        logger.warning("Invalid or empty input received.")
        return {"trick": "Invalid input."}

    if type in [TrickType.actors, TrickType.cricketers, TrickType.animals, TrickType.professions]:
        trick = handle_entity_based_trick(type.value, input_parts)
        return {"trick": trick}

    elif type == TrickType.simple_sentence:
        if wordbank_cache is None:
            wordbank_cache = load_wordbank_file()
            logger.debug("Wordbank loaded into cache.")
        template_file = TEMPLATE_FILE_MAP.get(type.value)
        templates = load_template_sentences(template_file)

        if not templates:
            logger.warning("No templates found for simple_sentence.")
            return {"trick": "No templates found for simple_sentence."}

        template = random.choice(templates)
        logger.debug(f"Using template: {template}")
        sentence = generate_template_sentence(template, wordbank_cache, [l.upper() for l in input_parts])
        return {"trick": sentence}

    elif type == TrickType.abbreviations:
        entities = load_entities("abbreviations")
        query = ''.join(input_parts).lower()
        matched = [e for e in entities if e.get("abbr", "").lower() == query]
        if not matched:
            logger.info(f"No abbreviation matched for query: {query}")
            return {"trick": f"No abbreviation found for '{query.upper()}'."}
        result = matched[0]
        return {"trick": f"{result['abbr']} — {result['full_form']}: {result['description']}"}

    return {"trick": "Invalid type selected."}

@router.get("/api/trick-basic")
def get_basic_trick(type: str, letter: str = "", name: str = ""):
    letters = letter.split(",")

    if type == "simple_sentence":
        wordbank = load_wordbank_file()
        templates = load_template_sentences(TEMPLATE_FILE_MAP["simple_sentence"])
        template = random.choice(templates)
        return {"sentence": generate_template_sentence(template, wordbank, letters)}

    elif type in ["actors", "cricketers", "animals"]:
        path = BASE_DIR / f"{type}.json"
        if not path.exists():
            logger.warning(f"Data file missing for type: {type} at {path}")
            return {"error": f"Data file for {type} not found."}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"sentence": generate_fixed_lines_sentence(name, data)}

    else:
        logger.warning(f"Invalid or unhandled type in basic trick endpoint: {type}")
        return {"error": "Invalid type or not implemented"}
