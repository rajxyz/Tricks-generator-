import json
import os
import random
from fastapi import APIRouter, Query
from collections import defaultdict

router = APIRouter()

Persistent actor selection tracking

actor_index = defaultdict(int)

def load_templates(): templates_path = os.path.join(os.path.dirname(os.path.abspath(file)), "..", "templates.json") with open(templates_path, "r", encoding="utf-8") as f: templates = json.load(f) return templates

def load_actors(letter=None): file_path = os.path.join(os.path.dirname(os.path.abspath(file)), "..", "bollywood-actor.json") with open(file_path, "r", encoding="utf-8") as f: actors = json.load(f)

if letter:
    actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

return actors

def get_next_actors(letters): selected_actors = [] for letter in letters: actors = load_actors(letter) if actors: index = actor_index[letter] % len(actors) selected_actors.append(actors[index]) actor_index[letter] += 1 return selected_actors

def generate_trick_sentence(actors, templates): if not actors: return "No actors found for the entered letters."

num_actors = len(actors)
template_category = f"{min(num_actors, 3)}_name_templates"

if template_category not in templates or not templates[template_category]:
    return "No templates available."

template = random.choice(templates[template_category])
actor_names = [f"<b>{actor['name']}</b>" for actor in actors]  # Highlight names

sentence = template["template"]
for i, name in enumerate(actor_names[:3]):
    sentence = sentence.replace(f"{{name{i+1}}}", name)

if "rhyming_words" in template and template["rhyming_words"]:
    rhyming_pair = random.choice(template["rhyming_words"])
    sentence += " " + " ".join(rhyming_pair)

return sentence

@router.get("/api/tricks") def get_tricks( type: str = Query(None, description="Type of trick (e.g., actors, cricketers)"), letter: str = Query(None, description="Comma-separated letters") ): templates = load_templates() letters = letter.upper().replace(" ", "").split(",") if letter else []

if type == "actors":
    actors = get_next_actors(letters)
    trick_sentence = generate_trick_sentence(actors, templates)
    return {"trick": trick_sentence}

return {"message": "Invalid type selected."}

