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
    print(f"[DEBUG] Loading templates for type: {trick_type} from {templates_path}")

    if not os.path.exists(templates_path):
        print(f"[ERROR] {filename} not found at {templates_path}")
        return {}

    with open(templates_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    print(f"[DEBUG] Loaded {len(templates)} templates for {trick_type}")
    return {key.lower(): val for key, val in templates.items()}

def load_actors(letter=None):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bollywood-actor.json")
    print(f"[DEBUG] Loading actors for letter: {letter} from {file_path}")

    if not os.path.exists(file_path):
        print(f"[ERROR] bollywood-actor.json not found at {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        actors = json.load(f)

    if letter:
        actors = [actor for actor in actors if actor.get("name", "").upper().startswith(letter.upper())]

    print(f"[DEBUG] Found {len(actors)} actors for letter {letter}")
    return actors

def get_next_actors(letters):
    print(f"[DEBUG] Getting next actors for letters: {letters}")
    selected_actors = []
    for letter in letters:
        actors = load_actors(letter[0])  # Use first character of word
        if actors:
            index = actor_index[letter] % len(actors)
            selected = actors[index]
            selected_actors.append(selected)
            actor_index[letter] += 1
            print(f"[DEBUG] Selected actor: {selected['name']} (index: {index})")
        else:
            print(f"[WARN] No actors found for letter: {letter}")
    return selected_actors

def generate_trick_with_topic(topic, actors, templates):
    if not actors:
        print("[WARN] No actors to generate trick with topic")
        return f"{topic}: {random.choice(default_lines)}"

    names = [actor.get("name", "") for actor in actors]
    joined_names = ", ".join(names)
    last_actor = names[-1].lower()

    print(f"[DEBUG] Generating trick for topic: {topic}, actors: {joined_names}, key: {last_actor}")
    if last_actor in templates:
        line = random.choice(templates[last_actor])
        print(f"[DEBUG] Found template line: {line}")
    else:
        line = random.choice(default_lines)
        print("[WARN] No template found, using default line")

    return f"<b>{topic}</b>, {joined_names}: {line}"

def generate_trick_sentence(actors, templates):
    if not actors:
        print("[WARN] No actors found to generate sentence")
        return "No actors found for the entered letters."

    names = [actor.get("name", "") for actor in actors]
    combined = ", ".join(names)
    last_actor = names[-1].lower()

    print(f"[DEBUG] Generating trick sentence for actors: {combined}, key: {last_actor}")
    if last_actor in templates:
        line = random.choice(templates[last_actor])
        print(f"[DEBUG] Found template line: {line}")
    else:
        line = random.choice(default_lines)
        print("[WARN] No template found, using default line")

    return f"{combined}: {line}"

@router.get("/api/tricks")
def get_tricks(
    type: str = Query("actors", description="Type of trick (e.g., actors, cricketers, animals)"),
    letters: str = Query(None, description="Comma-separated letters or words")
):
    print(f"[INFO] Request received: type={type}, letters={letters}")
    templates = load_templates(type)

    input_parts = letters.split(",") if letters else []
    input_parts = [w.strip() for w in input_parts if w.strip()]

    if not input_parts:
        print("[ERROR] No valid input letters provided")
        return {"trick": "Invalid input."}

    # Letter-based or word-based logic
    if type in ["actors", "cricketers", "animals"]:
        if all(len(word) == 1 for word in input_parts):
            print(f"[INFO] Letter-based trick requested")
            actors = get_next_actors(input_parts)
            print(f"[DEBUG] Selected actors: {[a['name'] for a in actors]}")
            trick = generate_trick_sentence(actors, templates)
            print(f"[INFO] Generated trick: {trick}")
            return {"trick": trick}
        else:
            topic = input_parts[0]
            rest_letters = [w.strip()[0].upper() for w in input_parts[1:]]
            print(f"[INFO] Word-based trick: topic={topic}, letters={rest_letters}")
            actors = get_next_actors(rest_letters)
            print(f"[DEBUG] Selected actors: {[a['name'] for a in actors]}")
            trick = generate_trick_with_topic(topic, actors, templates)
            print(f"[INFO] Generated trick: {trick}")
            return {"trick": trick}

    print("[ERROR] Invalid type selected")
    return {"message": "Invalid type selected."}
