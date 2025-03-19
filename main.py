from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
headers = {"Authorization": f"Bearer YOUR_HF_API_TOKEN"}

class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def root():
    return {"message": "Memory Trick Generator is running."}

@app.post("/generate_trick/")
def generate_trick(request: TrickRequest):
    try:
        prompts = {
            "acronym": f"Create a meaningful acronym using the concept: {request.concept}. It should form a word easy to remember.",
            "acrostic": f"Make a meaningful sentence (Acrostic) using each letter of: {request.concept}. The sentence should help memorize it.",
            "rhymes_songs": f"Write a short, catchy rhyme or song lyrics to help memorize the concept: {request.concept}.",
            "visualization": f"Describe a strong and vivid visual image that can help recall the concept: {request.concept}.",
            "method_of_loci": f"Use the Method of Loci technique to link the concept {request.concept} with familiar locations.",
            "association": f"Create a strong mental association between {request.concept} and something commonly seen or used daily.",
            "peg_system": f"Use the Peg System to link each item in {request.concept} with pegs like 1-Sun, 2-Shoe, etc.",
            "key_words_method": f"Use the Key Words Method to simplify and help memorize the concept {request.concept} using familiar keywords.",
        }

        trick_type = request.trick_type.lower()
        if trick_type not in prompts:
            raise HTTPException(status_code=400, detail="Invalid trick type.")

        payload = {
            "inputs": prompts[trick_type],
            "parameters": {"max_new_tokens": 100}
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Model API Error")

        result = response.json()
        output = result[0]["generated_text"].replace(prompts[trick_type], "").strip()

        return {
            "concept": request.concept,
            "trick_type": request.trick_type,
            "trick": output
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
