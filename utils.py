import json
import os
from config import DATA_PATH

def load_data(file_name):
    """Load JSON data from a given file safely."""
    file_path = os.path.join(DATA_PATH, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
