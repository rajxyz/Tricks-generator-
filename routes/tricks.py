import json import os import random from fastapi import APIRouter, Query from collections import defaultdict from pathlib import Path

from sentence_rules import generate_grammar_sentence

router = APIRouter() actor_index = defaultdict(int)

default_lines = [ "Iska trick abhi update nahi hua.", "Agle version me iski baari aayegi.", "Filhal kuch khaas nahi bola ja sakta.", "Yeh abhi training me hai, ruk ja thoda!" ]

TEMPLATE_FILE_MAP = { "actors": "Actor-templates.json", "cricketers": "Cricketers-templates.json", "animals": "Animals-templates.json" }

def load_templates(trick_type="actors"): filename = TEMPLATE_FILE_MAP.get(trick_type.lower(), "templates.json") templates_path = os.path.join(os.path.dirname(os.path.abspath(file)), "..", filename)

if not os.path.exists(templates_path):
    print(f"Warning: {filename} not found at {templates_path}")
    return {}

with open(templates_path, "r", encoding="utf-8") as f:
    templates = json.load(f)

print(f"Loaded templates for: {trick_type} -> {len(templates)} entries.")
return {key.lower(): val for key, val in templates.items()}

def load_actors(letter=None): file_path = os.path.join(os.path.dirname(os.path.abspath(file)), "..", "bollywood-actor.json")

if not os.path.exists(file_path):
    print(f"Warning: bollywood-actor.json not found at {file_path}")
    return []

with open(file_path, "r", encoding="utf-8") as f:
    actors = json.load(f)

if letter:
    actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

# Extract first name only
for actor in actors:
    actor["name"] = actor.get("name", "").split()[0]

print(f"Loaded {len(actors)} actors for letter: {letter}")
return actors

def get_next_actors(letters): selected_actors = [] for letter in letters: actors = load_actors(letter[0]) if actors: index = actor_index[letter] % len(actors) selected_actors.append(actors[index]) actor_index[letter] += 1 return selected_actors

Updated: Generate trick with topic considering first name only

