import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict

router = APIRouter()
item_index = defaultdict(int)

def load_templates(trick_type: str):
    """Load templates based on type from JSON file."""
    filename = f"{trick_type.capitalize()}-templates.json"
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(templates_path):
        print(f"Warning: {filename} not found at {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"Loaded {len(templates)} templates for type: {trick_type}")
    return templates

def load_data(trick_type: str, letter: str):
    """Load data (e.g., actors, cricketers) from file and filter by starting letter."""
    file_mapping = {
        "actors": "bollywood-actor.json",
        "cricketers": "cricketor.json",
        "animals": "animal.json",
    }

    filename = file_mapping.get(trick_type.lower())
    if not filename:
        print(f"Unsupported type: {trick_type}")
        return []

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)

    if not os.path.exists(file_path):
        print(f"Warning: {filename} not found at {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if letter:
        data = [item for item in data if item.get("name", "").upper().startswith(letter.upper())]

    print(f"Loaded {len(data)} items for type: {trick_type}, letter: {letter}")
    return data

def get_next_items(trick_type: str, letters):
    """Fetch the next available item (actor/cricketer/animal) for each letter."""
    selected_items = []
    for letter in letters:
        items = load_data(trick_type, letter)
        if items:
            index = item_index[letter] % len(items)
            selected_items.append(items[index])
            item_index[letter] += 1
    return selected_items

def generate_trick_sentence(items, templates):
    """Generate a trick sentence using selected items and a template."""
    if not items:
        return "No items found for the entered letters."

    num_items = len(items)
    template_category = f"{min(num_items, 3)}_name_templates"

    if template_category not in templates or not templates[template_category]:
        return "No templates available."

    template = random.choice(templates[template_category])
    item_names = [f"<b>{item['name']}</b>" for item in items]

    sentence = template["template"]
    for i, name in enumerate(item_names[:3]):
        sentence = sentence.replace(f"{{name{i+1}}}", name)

    if "rhyming_words" in template and template["rhyming_words"]:
        rhyming_pair = random.choice(template["rhyming_words"])
        sentence += " " + " ".join(rhyming_pair)

    return sentence

@router.get("/api/tricks")
def get_tricks(
    type: str = Query(None, description="Type of trick (e.g., actors, cricketers, animals)"),
    letter: str = Query(None, description="Comma-separated letters")
):
    print(f"Request received: type={type}, letter={letter}")

    if not type:
        return {"message": "Type is required."}

    templates = load_templates(type)
    letters = letter.upper().replace(" ", "").split(",") if letter else []

    items = get_next_items(type, letters)
    print(f"Selected items: {items}")

    trick_sentence = generate_trick_sentence(items, templates)
    print(f"Generated trick: {trick_sentence}")

    return {"trick": trick_sentence}
