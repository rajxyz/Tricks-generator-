from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Hugging Face Inference API URL for the "distilgpt2" model
API_URL = "https://api-inference.huggingface.co/models/distilgpt2"

# If you have an API token from Hugging Face, paste it here.
# Sign up at https://huggingface.co and get your token from your profile settings.
API_TOKEN = ""  # Replace with your token if available

# If API_TOKEN is set, include the authorization header; otherwise, leave headers empty.
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
            "acronym": f"Create an acronym for: {request.concept}.",
            "acrostic": f"Make a sentence where each word starts with letters from: {request.concept}.",
            "visualization": f"Visualize and describe: {request.concept}.",
        }
        # Default prompt if trick_type doesn't match any key
        prompt = prompts.get(request.trick_type.lower(), f"Memory trick for: {request.concept}.")

        # Send request to Hugging Face Inference API
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code != 200:
            raise Exception("Hugging Face API error: " + response.text)

        output = response.json()
        # Assuming the response returns a list of generated outputs
        generated_text = output[0].get("generated_text", "")
        # Remove the prompt part from the generated text
        trick = generated_text.replace(prompt, "").strip()
        return {"concept": request.concept, "trick_type": request.trick_type, "trick": trick}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
