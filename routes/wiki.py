from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from wiki_utils import fetch_wikipedia_summary  # Corrected import

router = APIRouter()


class WikiRequest(BaseModel):
    titles: List[str]


@router.post("/wiki-summary")
async def get_wiki_summary(request: WikiRequest):
    summaries = {}
    for title in request.titles:
        summary = fetch_wikipedia_summary(title)
        summaries[title] = summary
    return summaries
