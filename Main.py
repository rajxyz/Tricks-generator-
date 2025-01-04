from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import random

app = FastAPI()

# Load GPT-2 model and tokenizer
model_name = "gpt2-hinglish-finetuned"  # Replace with your model name
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Data structure for request body
class TrickRequest(BaseModel):
    concept: str  # The concept or word (e.g., "Stomach enzymes")
    trick_type: str  # The type of trick (e.g., Acronym, Acrostic, etc.)

# Generate trick
def generate_trick(concept: str, trick_type: str) -> str:
    try:
        # Define prompt based on trick type
        prompts = {
            "acronym": f"Create a Hinglish acronym for: {concept}. Add humor and real-world examples.",
            "acrostic": f"Generate a Hinglish acrostic sentence for: {concept}. Make it creative and relatable.",
            "song_rhyme": f"Write a Hinglish rhyme to remember: {concept}. Keep it funny and creative.",
            "visualization": f"Describe a visual trick in Hinglish to remember: {concept}.",
            "association": f"Create a Hinglish association for: {concept}. Add humor and cultural relevance.",
        }
        
        # Select appropriate prompt
        prompt = prompts.get(trick_type.lower(), f"Generate a Hinglish trick for: {concept}.")

        # Generate text using GPT-2
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=0.8, top_p=0.9)
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

        # Post-process generated text
        trick = generated_text.replace(prompt, "").strip()
        return trick

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Endpoint
@app.post("/generate_trick/")
def create_trick(request: TrickRequest):
    concept = request.concept
    trick_type = request.trick_type
    return {"concept": concept, "trick_type": trick_type, "trick": generate_trick(concept, trick_type)}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
