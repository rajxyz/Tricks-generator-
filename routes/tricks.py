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
    logger.debug(f"Loading entities for trick_type={trick_type}, letter={letter}")
    filename = DATA_FILE_MAP.get(trick_type.lower())
    if not filename:
        logger.debug(f"No data file mapping found for trick_type={trick_type}")
        return []

    file_path = BASE_DIR / filename
    if not file_path.exists():
        logger.warning(f"Entity data file not found: {file_path}")
        return []

    with file_path.open("r", encoding="utf-8") as f:
        entities = json.load(f)

    if letter and trick_type != "abbreviations":
        entities = [e for e in entities if e.get("name", "").upper().startswith(letter.upper())]

    logger.debug(f"Loaded {len(entities)} entities")
    return entities

# Load wordbank for simple_sentence
def load_wordbank_file():
    logger.debug("Loading wordbank file for simple_sentence")
    file_path = BASE_DIR / DATA_FILE_MAP["simple_sentence"]
    if not file_path.exists():
        logger.warning(f"Wordbank file not found: {file_path}")
        return {}
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    logger.debug(f"Loaded wordbank with {len(data)} entries")
    return data

# Get next entity based on letter
def get_next_entities(trick_type, letters):
    logger.debug(f"Getting next entities for trick_type={trick_type}, letters={letters}")
    selected = []
    for letter in letters:
        entities = load_entities(trick_type, letter[0])
        if entities:
            index = entity_index[(trick_type, letter)] % len(entities)
            logger.debug(f"Selected entity index={index} for letter={letter}")
            selected.append(entities[index])
            entity_index[(trick_type, letter)] += 1
        else:
            logger.debug(f"No entities found for letter={letter}")
    logger.debug(f"Selected entities: {selected}")
    return selected

# Logic for actor/cricketer/animal/profession style tricks
def handle_entity_based_trick(type, input_parts):
    logger.debug(f"Handling entity based trick for type={type} with input_parts={input_parts}")
    template_file = TEMPLATE_FILE_MAP.get(type)
    templates = load_template_sentences(template_file)
    logger.debug(f"Loaded templates: {len(templates)}")

    if all(len(w) == 1 for w in input_parts):
        entities = get_next_entities(type, input_parts)
        trick_sentence = generate_trick_sentence(entities, templates)
        logger.debug(f"Generated trick sentence: {trick_sentence}")
        return trick_sentence
    else:
        topic = input_parts[0]
        rest_letters = [w[0].upper() for w in input_parts[1:] if w]
        logger.debug(f"Topic: {topic}, rest_letters: {rest_letters}")
        entities = get_next_entities(type, rest_letters)
        trick_sentence = generate_trick_with_topic(topic, entities, templates)
        logger.debug(f"Generated trick with topic: {trick_sentence}")
        return trick_sentence

# Generate sentence from templates for entity types
def generate_trick_sentence(entities, templates):
    logger.debug(f"Generating trick sentence from entities: {entities}")
    if not entities:
        logger.debug("No entities passed to generate_trick_sentence")
        return "No names found for the entered letters."

    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        logger.debug("No valid names found in entities")
        return "Entity names missing or malformed."

    last_name = names[-1].lower()
    line = random.choice(templates.get(last_name, default_lines))
    result = f"{', '.join(names)}: {line}"
    logger.debug(f"Generated sentence: {result}")
    return result

# Generate with topic
def generate_trick_with_topic(topic, entities, templates):
    logger.debug(f"Generating trick with topic='{topic}', entities={entities}")
    if not entities:
        line = f"{topic}: {random.choice(default_lines)}"
        logger.debug(f"No entities found, returning line: {line}")
        return line
    names = [e.get("name", "") for e in entities if e.get("name")]
    if not names:
        line = f"{topic}: Entity names missing or malformed."
        logger.debug(line)
        return line
    last_entity = names[-1].lower()
    line = random.choice(templates.get(last_entity, default_lines))
    result = f"<b>{topic}</b>, {', '.join(names)}: {line}"
    logger.debug(f"Generated trick with topic: {result}")
    return result

# Main route
@router.get("/api/tricks")
def get_tricks(
    type: TrickType = Query(TrickType.actors, description="Type of trick"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    global wordbank_cache

    logger.debug(f"API call to /api/tricks with type={type}, letters={letters}")

    input_parts = [w.strip() for w in letters.split(",")] if letters else []
    input_parts = [w for w in input_parts if w]

    logger.debug(f"Parsed input_parts: {input_parts}")

    if not input_parts:
        logger.debug("Invalid input: No letters provided")
        return {"trick": "Invalid input."}

    # 1st Group: actors, cricketers, animals, professions
    if type in [TrickType.actors, TrickType.cricketers, TrickType.animals, TrickType.professions]:
        logger.debug(f"Processing entity-based trick for type={type}")
        trick = handle_entity_based_trick(type.value, input_parts)
        logger.debug(f"Returning trick: {trick}")
        return {"trick": trick}

    # 2nd Group: simple_sentence
    elif type == TrickType.simple_sentence:
        logger.debug("Processing simple_sentence trick")
        if wordbank_cache is None:
            logger.debug("Wordbank cache empty, loading wordbank")
            wordbank_cache = load_wordbank_file()
        template_file = TEMPLATE_FILE_MAP.get(type.value)
        templates = load_template_sentences(template_file)

        if not templates:
            logger.debug("No templates found for simple_sentence")
            return {"trick": "No templates found for simple_sentence."}

        template = random.choice(templates)
        logger.debug(f"Selected template: {template}")
        sentence = generate_template_sentence(template, wordbank_cache, [l.upper() for l in input_parts])
        logger.debug(f"Generated sentence: {sentence}")
        return {"trick": sentence}

    # 3rd Group: abbreviation (untouched as requested)
    elif type == TrickType.abbreviations:
        logger.debug("Processing abbreviations trick")
        entities = load_entities("abbreviations")
        query = ''.join(input_parts).lower()
        logger.debug(f"Query abbreviation: {query}")
        matched = [e for e in entities if e.get("abbr", "").lower() == query]
        if not matched:
            logger.debug(f"No abbreviation found for '{query.upper()}'")
            return {"trick": f"No abbreviation found for '{query.upper()}'."}
        result = matched[0]
        trick_result = f"{result['abbr']} — {result['full_form']}: {result['description']}"
        logger.debug(f"Found abbreviation: {trick_result}")
        return {"trick": trick_result}

    logger.debug("Invalid type selected")
    return {"trick": "Invalid type selected."}

# Additional endpoint to support basic generation
@router.get("/api/trick-basic")
def get_basic_trick(type: str, letter: str = "", name: str = ""):
    logger.debug(f"API call to /api/trick-basic with type={type}, letter={letter}, name={name}")
    letters = letter.split(",")

    if type == "simple_sentence":
        logger.debug("Generating basic simple_sentence trick")
        wordbank = load_wordbank_file()
        templates = load_template_sentences(TEMPLATE_FILE_MAP["simple_sentence"])
        template = random.choice(templates)
        sentence = generate_template_sentence(template, wordbank, letters)
        logger.debug(f"Generated sentence: {sentence}")
        return {"sentence": sentence}

    elif type in ["actors", "cricketers", "animals"]:
        logger.debug(f"Generating basic trick for type={type}")
        path = BASE_DIR / f"{type}.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sentence = generate_fixed_lines_sentence(name, data)
        logger.debug(f"Generated sentence: {sentence}")
        return {"sentence": sentence}

    else:
        logger.debug(f"Invalid type or not implemented for basic trick: {type}")
        return {"error": "Invalid type or not implemented"}
