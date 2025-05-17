import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict
from pathlib import Path

from routes.generate_template_sentence import generate_template_sentence

router = APIRouter()
entity_index = defaultdict(int)

default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json",
    "english_template_sentences": "English-templates.json"
}

DATA_FILE_MAP = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json"
}


def load_templates(trick_type="actors"):
    filename = TEMPLATE_FILE_MAP.get(trick_type.lower())
    if not filename:
        return {}

    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(templates_path):
        print(f"Warning: {filename} not found at {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"Loaded templates for: {trick_type} -> {len(templates)} entries.")

    if trick_type == "english_template_sentences":
        return templates.get("TEMPLATES", [])
    else:
        return {key.lower(): val for key, val in templates.items()}


def load_entities(trick_type, letter=None):
    filename = DATA_FILE_MAP.get(trick_type.lower())
    if not filename:
        return []

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(file_path):
        print(f"Warning: {filename} not found at {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        entities = json.load(f)

    if letter:
        entities = [entity for entity in entities if entity.get("name", "").upper().startswith(letter.upper())]

    print(f"Loaded {len(entities)} {trick_type} for letter: {letter}")
    return entities


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

    names = [e.get("name", "") for e in entities]
    joined_names = ", ".join(names)
    last_entity = names[-1].lower()

    if last_entity in templates:
        line = random.choice(templates[last_entity])
    else:
        line = random.choice(default_lines)

    return f"<b>{topic}</b>, {joined_names}: {line}"


def generate_trick_sentence(entities, templates):
    if not entities:
        return "No names found for the entered letters."

    names = [e.get("name", "") for e in entities]
    combined = ", ".join(names)
    last_name = names[-1].lower()

    if last_name in templates:
        line = random.choice(templates[last_name])
    else:
        line = random.choice(default_lines)

    return f"{combined}: {line}"


@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers, animals, english_template_sentences)"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    print(f"Request received: type={type}, letters={letters}")
    
    input_parts = letters.split(",") if letters else []
    input_parts = [w.strip() for w in input_parts if w.strip()]

    if not input_parts:
        return {"trick": "Invalid input."}

    if type in ["actors", "cricketers", "animals"]:
        templates = load_templates(type)

        if all(len(w) == 1 for w in input_parts):
            entities = get_next_entities(type, input_parts)
            trick = generate_trick_sentence(entities, templates)
            return {"trick": trick}
        else:
            topic = input_parts[0]
            rest_letters = [w[0].upper() for w in input_parts[1:] if w]
            entities = get_next_entities(type, rest_letters)
            trick = generate_trick_with_topic(topic, entities, templates)
            return {"trick": trick}

    elif type == "english_template_sentences":
        wordbank_path = Path(__file__).parent.parent / "wordbank.json"
        grammar_path = Path(__file__).parent.parent / "grammar_helpers.json"

        if not wordbank_path.exists():
            return {"trick": "Wordbank file missing."}
        if not grammar_path.exists():
            return {"trick": "Grammar helpers file missing."}

        with open(wordbank_path, "r", encoding="utf-8") as f:
            wordbank = json.load(f)
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar_helpers = json.load(f)

        grammar_helpers = {k.lower(): v for k, v in grammar_helpers.items()}

        templates = load_templates("english_template_sentences")
        if not templates:
            return {"trick": "English templates file missing."}

        template = random.choice(templates)
        trick = generate_template_sentence(template, grammar_helpers, wordbank, input_parts)

        # **Fix here: return the generated trick instead of the invalid message**
        return {"trick": trick}

    else:
        return {"trick": "Invalid type selected."}
