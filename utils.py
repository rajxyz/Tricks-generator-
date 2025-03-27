import json
from config import DATA_PATH

def load_data(file_name):
    """Load JSON data from a given file."""
    with open(DATA_PATH + file_name, "r", encoding="utf-8") as file:
        return json.load(file)
