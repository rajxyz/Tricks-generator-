from fastapi import APIRouter
from utils import load_data

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/{category}/{letter}")
def search_by_letter(category: str, letter: str):
    """Search for names starting with a given letter."""
    try:
        data = load_data(f"{category}.json")
        filtered_data = [item for item in data if item.lower().startswith(letter.lower())]
        return {"letter": letter, "results": filtered_data}
    except FileNotFoundError:
        return {"error": "Category not found"}
