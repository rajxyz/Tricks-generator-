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

        return entities

    except Exception as e:
        logger.exception(f"Error loading entities for {trick_type} with letter {letter}: {e}")
        return []

def load_wordbank_file():
    try:
        file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
        if not file_path.exists():
            logger.error(f"Wordbank file not found: {file_path}")
            return {}

        with file_path.open("r", encoding="utf-8") as f:
            wordbank = json.load(f)

        return wordbank

    except Exception as e:
        logger.exception(f"Error loading wordbank file: {e}")
        return {}

wordbank_cache = None

def get_next_entities(trick_type, letters):
    selected = []
    for letter in letters:
        entities = load_entities(trick_type, letter[0])
        if entities:
            idx = entity_index[(trick_type, letter)] % len(entities)
            selected.append(entities[idx])
            entity_index[(trick_type, letter)] += 1
        else:
            logger.debug(f"No entities found for letter '{letter}' in trick_type '{trick_type}'")
    return selected

def generate_trick_sentence(entities, templates):
    try:
        if not entities:
            return "No names found for the entered letters."

        names = [e.get("name", "") for e in entities if e.get("name")]
        if not names:
            return "Entity names missing or malformed."

        last_name = names[-1].lower()
        line = random.choice(templates.get(last_name, default_lines))
        return f"{', '.join(names)}: {line}"

    except Exception as e:
        logger.exception(f"Error generating trick sentence: {e}")
        return "Error generating trick."

def generate_trick_with_topic(topic, entities, templates):
    try:
        if not entities:
            return f"{topic}: {random.choice(default_lines)}"

        names = [e.get("name", "") for e in entities if e.get("name")]
        if not names:
            return f"{topic}: Entity names missing or malformed."

        last_entity = names[-1].lower()
        line = random.choice(templates.get(last_entity, default_lines))
        return f"<b>{topic}</b>, {', '.join(names)}: {line}"

    except Exception as e:
        logger.exception(f"Error generating trick with topic '{topic}': {e}")
        return "Error generating trick with topic."

@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(TrickType.actors, description="Type of trick"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    global wordbank_cache

    try:
        logger.info(f"Request received: type={type}, letters={letters}")

        input_parts = [w.strip() for w in letters.split(",")] if letters else []
        input_parts = [w for w in input_parts if w]

        if not input_parts:
            return {"trick": "Invalid input."}

        if type in [TrickType.actors, TrickType.cricketers, TrickType.animals, TrickType.professions]:
            template_file = TEMPLATE_FILE_MAP.get(type.value)
            template_path = BASE_DIR / template_file
            templates = load_template_sentences(template_path)

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

            template_file = TEMPLATE_FILE_MAP.get(type.value)
            template_path = BASE_DIR / template_file
            templates = load_template_sentences(template_path)

            if not templates:
                return {"trick": "No templates found for simple_sentence."}

            template = random.choice(templates)
            sentence = generate_template_sentence(
                template,
                wordbank_cache,
                [l.upper() for l in input_parts]
            )
            sentence = sentence[0].upper() + sentence[1:]
            if not sentence.endswith("."):
                sentence += "."

            return {"trick": sentence}

        else:
            return {"trick": "Invalid type selected."}

    except Exception as e:
        logger.exception(f"Error in get_tricks endpoint: {e}")
        return {"trick": "Server error while processing your request."}
    
