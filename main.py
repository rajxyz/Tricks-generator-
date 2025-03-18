from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
API_TOKEN = os.getenv("API_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}

class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def root():
    return {"status": "API is running!"}

@app.post("/generate_trick/")
def create_trick(request: TrickRequest):
    try:
        prompts = {
            "acronym": f"Create a meaningful acronym to remember: {request.concept}. Ensure it's easy to recall.",
            "acrostic": f"Make a meaningful sentence (Acrostic) where each word starts with letters from: {request.concept}.",
            "rhymes_songs": f"Write a short, catchy rhyme or song lyrics to memorize: {request.concept}.",
            "visualization": f"Describe a visual scene that strongly connects with: {request.concept}.",
            "method_of_loci": f"Use the Method of Loci to link {request.concept} with a familiar location for easy recall.",
            "association": f"Create a strong association between {request.concept} and something common in daily life.",
            "peg_system": f"Use the Peg System to remember {request.concept} by linking it with numbers (1 = Sun, 2 = Shoe, etc.).",
            "key_words_method": f"Generate a Key Words Method trick to help memorize {request.concept} by linking keywords.",
            "question": f"Generate a NEET-style question based on the concept: {request.concept}.",
        }

        prompt = prompts.get(request.trick_type.lower(), f"Generate a memory trick for: {request.concept}.")

        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code != 200:
            raise Exception("Hugging Face API error: " + response.text)

        output = response.json()
        generated_text = output[0].get("generated_text", "")
        trick = generated_text.replace(prompt, "").strip()

        return {
            "concept": request.concept,
            "trick_type": request.trick_type,
            "trick": trick
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Debug endpoint to test Hugging Face API connection
@app.get("/test_hf")
def test_hf():
    test_prompt = "Create a mnemonic for: Physics"
    response = requests.post(API_URL, headers=headers, json={"inputs": test_prompt})
    return {"status_code": response.status_code, "response": response.json()}
