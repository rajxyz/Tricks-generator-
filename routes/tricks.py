import json
import os
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/api/tricks")
def get_tricks(
    type: str = Query(None, description="Type of trick (e.g., actors, cricketers)"),
    letter: str = Query(None, description="Starting letter")
):
    data = []
    
    if type == "actors":
        # Adjust the file path based on your project structure.
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bollywood-actor.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Filter by starting letter if provided
            if letter:
                data = [actor for actor in data if actor.get("name", "").upper().startswith(letter.upper())]
        except Exception as e:
            return {"error": "Error reading actor data", "details": str(e)}
    
    # Optionally add similar logic for other types (e.g., cricketers)
    
    return data
