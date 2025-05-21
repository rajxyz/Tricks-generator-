import requests

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
    return None
