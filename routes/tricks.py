import json
import os
import random
import re
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

def extract_letters(input_str):
    input_str = re.sub(r"[^a-zA-Z,\s]", "", input_str).strip()

    if "," in input_str:
        parts = [p.strip() for p in input_str.split(",") if p.strip()]
        if all(len(p) > 1 for p in parts):
            return [p[0].upper() for p in parts]
        return [p.upper() for p in parts]

    if re.fullmatch(r"[a-zA-Z]+", input_str):
        if len(input_str) <= 5:
            return list(input_str.upper())
        return [ch[0].upper() for ch in re.findall(r'[A-Z][a-z]*', input_str) or input_str]

    words = re.findall(r'\b\w+', input_str)
    return [w[0].upper() for w in words if w]

def load_templates(category="actors"):
    filename = template_file_map.get(category.lower())
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filename)
    if not os.path.exists(path):
        print(f"Warning: {filename} not found at {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        templates = json.load(f)
    return {key.lower(): val for key, val in templates.items()}

def load_sentence_templates():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sentence_templates.json")
    if not os.path.exists(path):
        print("Warning: sentence_templates.json not found.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

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
    for letter in letters:
        entities = load_entities(category, letter[0])
        if entities:
            index = actor_index[(category, letter)] % len(entities)
            selected.append(entities[index])
            actor_index[(category, letter)] += 1
    return selected

def format_names(entities, category):
    if category == "cricketers":
        names = [e.get("name", "") for e in entities]
        if len(names) > 1:
            first_parts = [name.split()[0] for name in names[:-1]]
            first_parts.append(names[-1])
            return first_parts
        return names
    elif category == "actors":
        return [e.get("name", "").split()[0] for e in entities]
    else:
        return [e.get("name", "") for e in entities]

@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers, animals)"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    print(f"Request received: type={type}, letters={letters}")
    sentence_templates = load_sentence_templates()

    input_parts = extract_letters(letters or "")
    print(f"Parsed input letters: {input_parts}")

    if not input_parts:
        return {"trick": "Invalid input."}

    if all(len(ch) == 1 for ch in input_parts):
        entities = get_next_entities(input_parts, type)
        names = format_names(entities, type)
        available_templates = sentence_templates.get(type, [])

        if available_templates and 4 <= len(names) <= 8:
            idx = len(names) - 4
            templates = available_templates[idx] if idx < len(available_templates) else available_templates[-1]
            template = random.choice(templates)
            try:
                trick = template.format(*names)
            except IndexError:
                trick = "Not enough names to fill the template."
            return {"trick": trick}

        return {"trick": ", ".join(names)}
    else:
        return {"trick": "Word input not supported for sentence templates."}
                        
