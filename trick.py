from fastapi import APIRouter, HTTPException
from utils import load_data

router = APIRouter(prefix="/tricks", tags=["Tricks"])

@router.get("/{category}")
def get_trick(category: str):
    """Get tricks based on category like actors, cricketers, animals."""
    try:
        data = load_data(f"{category}.json")  # ✅ Load the relevant JSON file
        return {"category": category, "data": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Category not found")

@router.get("/{category}/{letter}")
def get_trick_by_letter(category: str, letter: str):
    """Get tricks filtered by the first letter."""
    try:
        data = load_data(f"{category}.json")
        filtered_data = {k: v for k, v in data.items() if k.upper().startswith(letter.upper())}

        if not filtered_data:
            return {"message": "No tricks found for this letter."}

        return {"category": category, "letter": letter, "data": filtered_data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Category not found")
