from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = FastAPI()

# Load GPT-2 model and tokenizer
model_name = "gpt2"  # Change if using a custom model
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Data structure for request body
class TrickRequest(BaseModel):
    concept: str  # The concept or topic (e.g., "Photosynthesis")
    trick_type: str  # The type of trick (e.g., "Acronym", "Visualization")

# Trick generation function
def generate_trick(concept: str, trick_type: str) -> str:
    try:
        # Trick prompts based on the selected method
        prompts = {
            "acronym": f"Create a meaningful acronym to remember: {concept}. Ensure it's easy to recall.",
            "acrostic": f"Make a meaningful sentence (Acrostic) where each word starts with letters from: {concept}.",
            "rhymes_songs": f"Write a short, catchy rhyme or song lyrics to memorize: {concept}.",
            "visualization": f"Describe a visual scene that strongly connects with: {concept}.",
            "method_of_loci": f"Use the Method of Loci to link {concept} with a familiar location for easy recall.",
            "association": f"Create a strong association between {concept} and something common in daily life.",
            "peg_system": f"Use the Peg System to remember {concept} by linking it with numbers (1 = Sun, 2 = Shoe, etc.).",
            "key_words_method": f"Generate a Key Words Method trick to help memorize {concept} by linking keywords."
        }

        # Get the appropriate prompt
        prompt = prompts.get(trick_type.lower(), f"Generate a memory trick for: {concept}.")

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
    return {
        "concept": request.concept,
        "trick_type": request.trick_type,
        "trick": generate_trick(request.concept, request.trick_type)
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
