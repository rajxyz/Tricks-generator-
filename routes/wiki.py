from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from routes.utils.wiki_utils import fetch_wikipedia_summary

router = APIRouter()
# rest of the code remains same
