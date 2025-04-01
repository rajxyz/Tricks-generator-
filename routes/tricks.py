import json
import os
import random
from fastapi import APIRouter, Query

router = APIRouter()

# Load templates for dynamic sentence generation (stored in a separate JSON file)
def load_templates():
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates.json")
    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)
    return templates

# Load actor names from the actor.json file
def load_actors(letter=None):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bollywood-actor.json")
    with open(file_path, "r", encoding="utf-8") as f:
        actors = json.load(f)

    # Filter actors by starting letter if provided
    if letter:
        actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

    return actors

# Function to generate a trick sentence
def generate_trick_sentence(actors, templates):
    if not actors:
        return "No actors found for this letter."

    num_actors = len(actors)

    # Select template category based on the number of actors
    template_category = f"{min(num_actors, 3)}_name_templates"

    if template_category not in templates or not templates[template_category]:
        return "No templates available for the selected number of actors."

    # Pick a random template from the correct category
    template = random.choice(templates[template_category])

    # Extract names
    actor_names = [actor["name"] for actor in actors]

    # Substitute names into the template
    sentence = template["template"]
    for i, name in enumerate(actor_names[:3]):  # Only use up to 3 actors
        sentence = sentence.replace(f"{{name{i+1}}}", name)

    # Add rhyming words if available
    if "rhyming_words" in template and template["rhyming_words"]:
        rhyming_pair = random.choice(template["rhyming_words"])
        sentence += " " + " ".join(rhyming_pair)

    return sentence

@router.get("/api/tricks")
def get_tricks(
    type: str = Query(None, description="Type of trick (e.g., actors, cricketers)"),
    letter: str = Query(None, description="Starting letter")
):
    templates = load_templates()

    if type == "actors":
        actors = load_actors(letter)
        trick_sentence = generate_trick_sentence(actors, templates)
        return {"trick": trick_sentence}

    return {"message": "No valid type selected."}
