import requests

def sanitize_abbreviation(term: str) -> str:
    # Remove commas and whitespace, then capitalize properly
    cleaned = term.replace(",", "").strip()
    return cleaned.capitalize() if len(cleaned) > 1 else cleaned.upper()

def fetch_abbreviation_details(abbreviation: str):
    term = sanitize_abbreviation(abbreviation)
    try:
        response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
        )
        data = response.json()
        if response.status_code == 200 and "title" in data and "extract" in data:
            # Extract only the main definition (1st sentence)
            main_fact = data["extract"].split(".")[0] + "."
            return {
                "abbr": abbreviation.upper(),
                "full_form": data["title"],
                "description": main_fact
            }
        else:
            return {
                "abbr": abbreviation.upper(),
                "full_form": "Not found",
                "description": "No definition found."
            }
    except Exception as e:
        return {
            "abbr": abbreviation.upper(),
            "full_form": "Error",
            "description": str(e)
        }
