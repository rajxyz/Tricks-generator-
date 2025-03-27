from fastapi import APIRouter
from utils import load_data

router = APIRouter(prefix="/tricks", tags=["Tricks"])

@router.get("/{category}")
def get_trick(category: str):
    """Get tricks based on category like actors, cricketers, animals."""
    try:
        data = load_data(f"{category}.json")
        return {"category": category, "data": data}
    except FileNotFoundError:
        return {"error": "Category not found"}
