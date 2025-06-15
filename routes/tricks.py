import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict

router = APIRouter()
actor_index = defaultdict(int)

default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

template_file_map = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json"
}

data_file_map = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json"
}

def load_templates(category="actors"):
    filename = template_file_map.get(category.lower())
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found at {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        templates = json.load(f)
    return {key.lower(): val for key, val in templates.items()}

def load_entities(category="actors", letter=None):
    filename = data_file_map.get(category.lower())
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if letter:
        return [d for d in data if d.get("name", "").upper().startswith(letter.upper())]
    return data

def get_next_entities(letters, category):
    selected = []
    for i, letter in enumerate(letters):
        entities = load_entities(category, letter[0])
        if entities:
            index = actor_index[letter] % len(entities)
            entity = entities[index]

            # Apply name/surname display rules
            if i == len(letters) - 1:
                # Last entity
                if category == "cricketers":
                    full_name = entity.get("name", "")
                    if "surname" in entity and entity["surname"]:
                        full_name += f" {entity['surname']}"
                    entity["_display"] = full_name.strip()
                else:  # actors, animals
                    entity["_display"] = entity.get("name", "")
            else:
                # First to third
                entity["_display"] = entity.get("name", "")

            selected.append(entity)
            actor_index[letter] += 1
    return selected

def find_template_key(name, templates):
    name_lower = name.lower()
    for key in templates:
        if key.lower() == name_lower:
            return key
        if key.lower() in name_lower or name_lower in key.lower():
            return key
    return None

def generate_trick_with_topic(topic, entities, templates):
    if not entities:
        return f"{topic}: {random.choice(default_lines)}"

    names = [e.get("_display", e.get("name", "")) for e in entities]

    if len(entities) > 4:
        sentence_templates = templates.get("_sentence", default_lines)
        line = random.choice(sentence_templates)
        return f"<b>{topic}</b>: {line.replace('{names}', ', '.join(names))}"

    joined_names = ", ".join(names)
    last_key = find_template_key(names[-1], templates)
    if last_key:
        line = random.choice(templates[last_key])
    else:
        line = random.choice(default_lines)
    return f"<b>{topic}</b>, {joined_names}: {line}"

def generate_trick_sentence(entities, templates):
    if not entities:
        return "No data found for the entered letters."

    names = [e.get("_display", e.get("name", "")) for e in entities]

    if len(names) > 4:
        sentence_templates = templates.get("_sentence", default_lines)
        line = random.choice(sentence_templates)
        return line.replace("{names}", ", ".join(names))

    combined = ", ".join(names)
    last_key = find_template_key(names[-1], templates)
    if last_key:
        line = random.choice(templates[last_key])
    else:
        line = random.choice(default_lines)
    return f"{combined}: {line}"

@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers, animals)"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    print(f"Request received: type={type}, letters={letters}")
    templates = load_templates(type)
    input_parts = letters.split(",") if letters else []
    input_parts = [w.strip() for w in input_parts if w.strip()]

    if not input_parts:
        return {"trick": "Invalid input."}

    if all(len(word) == 1 for word in input_parts):
        entities = get_next_entities(input_parts, type)
        trick = generate_trick_sentence(entities, templates)
        return {"trick": trick}
    else:
        topic = input_parts[0]
        rest_letters = [w[0].upper() for w in input_parts[1:]]
        entities = get_next_entities(rest_letters, type)
        trick = generate_trick_with_topic(topic, entities, templates)
        return {"trick": trick}
