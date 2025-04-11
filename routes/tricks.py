import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict

router = APIRouter()
actor_index = defaultdict(int)

def load_templates(trick_type="actors"):
    """Load templates from the appropriate JSON file based on trick type."""
    filename = f"{trick_type.capitalize()}-templates.json"
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(templates_path):
        print(f"Warning: {filename} not found at {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"Loaded templates for: {trick_type} -> {len(templates)} entries.")
    return templates

def load_actors(letter=None):
    """Load Bollywood actors from JSON file. Filter by starting letter if provided."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bollywood-actor.json")

    if not os.path.exists(file_path):
        print(f"Warning: bollywood-actor.json not found at {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        actors = json.load(f)

    if letter:
        actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

    print(f"Loaded {len(actors)} actors for letter: {letter}")
    return actors

def get_next_actors(letters):
    """Fetch the next available actor for each entered letter in a cyclic manner."""
    selected_actors = []
    for letter in letters:
        actors = load_actors(letter)
        if actors:
            index = actor_index[letter] % len(actors)
            selected_actors.append(actors[index])
            actor_index[letter] += 1
    return selected_actors

def generate_trick_sentence(actors, templates):
    """Generate trick lines using actor names and their template lines."""
    if not actors:
        return "No actors found for the entered letters."

    sentences = []
    for actor in actors:
        name = actor.get("name", "")
        if name in templates:
            line = random.choice(templates[name])
            sentences.append(f"<b>{name}</b>: {line}")
        else:
            sentences.append(f"<b>{name}</b>: No trick available.")
    
    return " | ".join(sentences)

@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers)"),
    letter: str = Query(None, description="Comma-separated letters")
):
    """API Endpoint to generate tricks based on user input."""
    print(f"Request received: type={type}, letter={letter}")

    templates = load_templates(type)
    letters = letter.upper().replace(" ", "").split(",") if letter else []

    if type == "actors":
        actors = get_next_actors(letters)
        print(f"Selected actors: {actors}")

        trick_sentence = generate_trick_sentence(actors, templates)
        print(f"Generated trick: {trick_sentence}")

        return {"trick": trick_sentence}

    return {"message": "Invalid type selected."}
