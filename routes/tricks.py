import json
import random
import logging
from fastapi import APIRouter, Query
from collections import defaultdict
from pathlib import Path
from enum import Enum

from routes.generate_template_sentence import (
  generate_template_sentence,
    load_templates as load_template_sentences
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
    simple_sentence = "simple_sentence"      # New trick type added


TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json",
    "simple_sentence": "English-templates.json"      # Template file for new trick
}

DATA_FILE_MAP = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json",
    "abbreviations": "data.json",
    "simple_sentence": "wordbank.json"                # Wordbank file for new trick
}


def load_templates(trick_type="actors"):
    filename = TEMPLATE_FILE_MAP.get(trick_type.lower())
    if not filename:
        return {}

    templates_path = BASE_DIR / filename
    if not templates_path.exists():
        logger.warning(f"Template file not found: {templates_path}")
        return {}

    with templates_path.open("r", encoding="utf-8") as f:
        templates = json.load(f)

    logger.info(f"Loaded templates for '{trick_type}' with {len(templates)} entries.")
    return {key.lower(): val for key, val in templates.items()}


def load_entities(trick_type, letter=None):
    filename = DATA_FILE_MAP.get(trick_type.lower())
    if not filename:
        return []

    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.warning(f"Entity data file not found: {file_path}")
        return []

    with file_path.open("r", encoding="utf-8") as f:
        entities = json.load(f)

    if letter and trick_type != "abbreviations":
        entities = [e for e in entities if e.get("name", "").upper().startswith(letter.upper())]

    logger.info(f"Loaded {len(entities)} {trick_type} for letter '{letter}'.")
    return entities


def load_wordbank_file():
    file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
    if not file_path.exists():
        logger.warning(f"Wordbank file not found: {file_path}")
        return {}

    with file_path.open("r", encoding="utf-8") as f:
        wordbank = json.load(f)
    return wordbank


wordbank_cache = None


def get_next_entities(trick_type, letters):
    selected = []
    for letter in letters:
        entities = load_entities(trick_type, letter[0])
        if entities:
            index = entity_index[(trick_type, letter)] % len(entities)
            selected.append(entities[index])
            entity_index[(trick_type, letter)] += 1
    return selected


def generate_trick_with_topic(topic, entities, templates):
    if not entities:
        return f"{topic}: {random.choice(default_lines)}"

    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        return f"{topic}: Entity names missing or malformed."

    last_entity = names[-1].lower()
    line = random.choice(templates.get(last_entity, default_lines))
    return f"<b>{topic}</b>, {', '.join(names)}: {line}"


def generate_trick_sentence(entities, templates):
    if not entities:
        return "No names found for the entered letters."

    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        return "Entity names missing or malformed."

    last_name = names[-1].lower()
    line = random.choice(templates.get(last_name, default_lines))
    return f"{', '.join(names)}: {line}"


@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(TrickType.actors, description="Type of trick"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    global wordbank_cache

    logger.info(f"Request received: type={type}, letters={letters}")

    input_parts = [w.strip() for w in letters.split(",")] if letters else []
    input_parts = [w for w in input_parts if w]

    if not input_parts:
        return {"trick": "Invalid input."}

    if type in [TrickType.actors, TrickType.cricketers, TrickType.animals]:
        templates = load_templates(type.value)

        if all(len(w) == 1 for w in input_parts):
            entities = get_next_entities(type.value, input_parts)
            trick = generate_trick_sentence(entities, templates)
        else:
            topic = input_parts[0]
            rest_letters = [w[0].upper() for w in input_parts[1:] if w]
            entities = get_next_entities(type.value, rest_letters)
            trick = generate_trick_with_topic(topic, entities, templates)

        return {"trick": trick}

    elif type == TrickType.abbreviations:
        entities = load_entities("abbreviations")
        query = ''.join(input_parts).lower()

        matched = [e for e in entities if e.get("abbr", "").lower() == query]

        if not matched:
            return {"trick": f"No abbreviation found for '{query.upper()}'."}

        result = matched[0]
        return {
            "trick": f"{result['abbr']} — {result['full_form']}: {result['description']}"
        }

    elif type == TrickType.simple_sentence:

        if wordbank_cache is None:
            wordbank_cache = load_wordbank_file()

        templates = load_template_sentences(type.value)

        template = random.choice(templates.get("templates", templates.get("TEMPLATES", [])))

        sentence = generate_template_sentence(
            template,
            wordbank_cache,
            [l.upper() for l in input_parts]
        )

        return {"trick": sentence}

    return {"trick": "Invalid type selected."}
