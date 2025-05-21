from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import requests
import json
from pathlib import Path

router = APIRouter()

CACHE_FILE = Path(__file__).parent.parent / "cache" / "abbreviations_cache.json"

class AbbrRequest(BaseModel):
    terms: List[str]

# Load cache from file
def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Save cache to file
def save_cache(cache_data):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def fetch_wikipedia_summary(term: str):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "abbr": term.upper(),
            "full_form": data.get("title", ""),
            "description": data.get("extract", "")
        }
    else:
        return None

@router.post("/fetch-abbreviations/")
def fetch_abbreviations(request: AbbrRequest):
    cache = load_cache()
    results = []

    for term in request.terms:
        term_upper = term.upper()
        if term_upper in cache:
            results.append(cache[term_upper])
        else:
            data = fetch_wikipedia_summary(term)
            if data:
                cache[term_upper] = data
                results.append(data)

    save_cache(cache)
    return {"fetched": results}
