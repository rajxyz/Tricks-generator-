import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict

router = APIRouter()
actor_index = defaultdict(int)

# Default fallback lines if no specific template is available
default_lines = [
    "Iska trick abhi update nahi hua.",
    "Agle version me iski baari aayegi.",
    "Filhal kuch khaas nahi bola ja sakta.",
    "Yeh abhi training me hai, ruk ja thoda!"
]

# Mapping correct filenames for templates
TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json"
}

# Mapping data files for items
DATA_FILE_MAP = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json"
}

def load_templates(trick_type="actors"):
    filename = TEMPLATE_FILE_MAP.get(trick_type.lower(), "templates.json")
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(templates_path):
        print(f"[WARN] Template file not found: {filename} at {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"[INFO] Loaded templates for: {trick_type} -> {len(templates)} entries.")
    return {key.lower(): val for key, val in templates.items()}

def load_items(letter=None, item_type="actors"):
    filename = DATA_FILE_MAP.get(item_type.lower())
    if not filename:
        print(f"[WARN] No data file configured for type: {item_type}")
        return []

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(file_path):
        print(f"[WARN] Data file not found: {filename} at {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    if letter:
        items = [item for item in items if item.get("name", "").upper().startswith(letter.upper())]

    print(f"[INFO] Loaded {len(items)} {item_type} for letter: {letter}")
    return items

def get_next_items(letters, item_type="actors"):
    selected = []
    for letter in letters:
        items = load_items(letter, item_type)
        if items:
            index = actor_index[letter] % len(items)
            selected.append(items[index])
            actor_index[letter] += 1
        else:
            print(f"[DEBUG] No {item_type} found for letter: {letter}")
    return selected

def generate_trick_sentence(items, templates):
    if not items:
        return "No entries found for the entered letters."

    sentences = []
    for item in items:
        name = item.get("name", "")
        lower_name = name.lower()

        if lower_name in templates:
            line = random.choice(templates[lower_name])
        else:
            line = random.choice(default_lines)

        sentences.append(f"<b>{name}</b>: {line}")

    return " | ".join(sentences)

@router.api_route("/api/tricks", methods=["GET", "POST"])
def get_tricks(
    type: str = Query("actors", description="Type of trick (actors, cricketers, animals)"),
    letters: str = Query(None, description="Comma-separated letters (e.g., A,B,C)")
):
    print(f"=== Incoming Request ===")
    print(f"[REQ] Type: {type}")
    print(f"[REQ] Letters: {letters}")

    templates = load_templates(type)
    print(f"[DEBUG] Loaded template keys: {list(templates.keys())[:5]}...")  # show first 5 keys

    letter_list = letters.upper().replace(" ", "").split(",") if letters else []
    print(f"[DEBUG] Parsed letters: {letter_list}")

    if type.lower() in ["actors", "cricketers", "animals"]:
        items = get_next_items(letter_list, type.lower())
        print(f"[DEBUG] Selected {type}: {[i.get('name', 'Unknown') for i in items]}")

        trick_sentence = generate_trick_sentence(items, templates)
        print(f"[RESULT] Trick Sentence: {trick_sentence}")

        return {"trick": trick_sentence}

    print("[ERROR] Invalid trick type selected.")
    return {"message": "Invalid type selected."}
