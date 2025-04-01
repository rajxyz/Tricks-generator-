import json
import os
import random
from fastapi import APIRouter, Query

router = APIRouter()

# Load templates for dynamic sentence generation (stored in a separate JSON file)
def load_templates():
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates.json")
    with open(templates_path, "r", encoding="utf-8") as f:
        return json.load(f)

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

    # Choose a random template
    template = random.choice(templates)
    
    # Substitute actors' names into the template
    actor_names = [actor["name"] for actor in actors]
    
    # Choose rhyming words dynamically
    rhyming_words = random.choice(template['rhyming']) if 'rhyming' in template else []

    # Create the sentence
    sentence = template["sentence"]
    sentence = sentence.replace("{actor1}", actor_names[0])
    
    if len(actor_names) > 1:
        sentence = sentence.replace("{actor2}", actor_names[1])

    if len(actor_names) > 2:
        sentence = sentence.replace("{actor3}", actor_names[2])

    # Add rhyming words if necessary
    for i, word in enumerate(rhyming_words):
        sentence += " " + word

    return sentence

@router.get("/api/tricks")
def get_tricks(
    type: str = Query(None, description="Type of trick (e.g., actors, cricketers)"),
    letter: str = Query(None, description="Starting letter")
):
    data = []
    templates = load_templates()  # Load templates from JSON file

    if type == "actors":
        # Load actors based on the starting letter
        actors = load_actors(letter)
        
        # Generate trick sentence using the selected actors and templates
        trick_sentence = generate_trick_sentence(actors, templates)

        # Return the generated trick sentence
        return {"trick": trick_sentence}
    
    # Optionally add similar logic for other types (e.g., cricketers)
    
    return {"message": "No valid type selected."}
