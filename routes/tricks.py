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

# Mapping correct filenames
TEMPLATE_FILE_MAP = {
    "actors": "Actor-templates.json",
    "cricketers": "Cricketers-templates.json",
    "animals": "Animals-templates.json"
}

def load_templates(trick_type="actors"):
    filename = TEMPLATE_FILE_MAP.get(trick_type.lower(), "templates.json")
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(templates_path):
        print(f"[WARN] Template file not found: {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"[INFO] Loaded {len(templates)} templates for type: {trick_type}")
    return {key.lower(): val for key, val in templates.items()}

def load_actors(letter=None):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bollywood-actor.json")

    if not os.path.exists(file_path):
        print(f"[WARN] Actor file not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        actors = json.load(f)

    if letter:
        actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

    print(f"[INFO] Loaded {len(actors)} actors for letter: {letter}")
    return actors

def get_next_actors(letters):
    selected_actors = []
    for letter in letters:
        actors = load_actors(letter)
        if actors:
            index = actor_index[letter] % len(actors)
            selected_actors.append(actors[index])
            actor_index[letter] += 1
        else:
            print(f"[DEBUG] No actors found for letter: {letter}")
    return selected_actors

def generate_trick_sentence(actors, templates):
    if not actors:
        print("[DEBUG] No actors found for the entered letters.")
        return "No actors found for the entered letters."

    sentences = []
    for actor in actors:
        name = actor.get("name", "")
        lower_name = name.lower()

        if lower_name in templates:
            print(f"[INFO] Template found for actor: {name}")
            line = random.choice(templates[lower_name])
        else:
            print(f"[INFO] No template found for actor: {name}. Using fallback line.")
            line = random.choice(default_lines)

        sentences.append(f"<b>{name}</b>: {line}")
    
    return " | ".join(sentences)

@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers)"),
    letters: str = Query(None, description="Comma-separated letters (e.g., A,B,C)")
):
    print("\n=== Incoming Request ===")
    print(f"[REQ] Type: {type}")
    print(f"[REQ] Letters: {letters}")

    templates = load_templates(type)
    print(f"[DEBUG] Loaded template keys: {list(templates.keys())[:5]}...")

    letter_list = letters.upper().replace(" ", "").split(",") if letters else []
    print(f"[DEBUG] Parsed letters: {letter_list}")

    if type == "actors":
        actors = get_next_actors(letter_list)
        print(f"[DEBUG] Selected actors: {[a.get('name', 'Unknown') for a in actors]}")

        trick_sentence = generate_trick_sentence(actors, templates)
        print(f"[RESULT] Trick Sentence: {trick_sentence}")

        return {"trick": trick_sentence}

    print("[ERROR] Invalid trick type selected.")
    return {"message": "Invalid type selected."}
