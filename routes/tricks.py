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

TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json"
}

DATA_FILE_MAP = {
    "actors": "bollywood-actor.json",
    "cricketers": "cricketers.json",
    "animals": "animals.json"
}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load_templates(trick_type="actors"):
    filename = TEMPLATE_FILE_MAP.get(trick_type.lower(), "")
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        print(f"[WARN] Template file not found: {path}")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"[INFO] Loaded templates for {trick_type}: {len(templates)} entries")
    return {k.lower(): v if isinstance(v, list) else [v] for k, v in templates.items()}

def load_items(letter=None, item_type="actors"):
    filename = DATA_FILE_MAP.get(item_type.lower())
    if not filename:
        print(f"[WARN] No data file for type: {item_type}")
        return []

    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARN] Data file not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    if letter:
        return [item for item in items if item.get("name", "").upper().startswith(letter.upper())]
    return items

def get_next_items(letters, item_type="actors"):
    selected = []
    for letter in letters:
        items = load_items(letter, item_type)
        if items:
            idx = actor_index[letter] % len(items)
            selected.append(items[idx])
            actor_index[letter] += 1
    return selected

def generate_trick_sentence(items, templates):
    if not items:
        return "No entries found for the entered letters."

    parts = []
    for item in items:
        name = item.get("name", "")
        lower = name.lower()
        line = random.choice(templates.get(lower, default_lines))
        parts.append(f"<b>{name}</b>: {line}")
    return " | ".join(parts)

@router.api_route("/api/tricks", methods=["GET", "POST"])
def get_tricks(
    type: str = Query("actors", description="Type of trick (actors, cricketers, animals)"),
    letters: str = Query(None, description="Comma-separated letters (e.g., A,B,C)")
):
    print(f"=== Incoming Request ===")
    print(f"[REQ] Type: {type}")
    print(f"[REQ] Letters: {letters}")

    templates = load_templates(type)
    letters_list = [l.strip().upper() for l in letters.replace(" ", "").split(",") if l.strip()] if letters else []

    print(f"[DEBUG] Parsed letters: {letters_list}")
    items = get_next_items(letters_list, type)
    print(f"[DEBUG] Selected: {[i.get('name') for i in items]}")

    trick = generate_trick_sentence(items, templates)
    print(f"[RESULT] Trick Sentence: {trick}")

    return {"trick": trick}
