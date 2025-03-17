from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = FastAPI()

model_name = "distilgpt2"  # Chhota aur lightweight
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def root():
    return {"status": "API is running!"}

@app.post("/generate_trick/")
def create_trick(request: TrickRequest):
    return {
        "concept": request.concept,
        "trick_type": request.trick_type,
        "trick": generate_trick(request.concept, request.trick_type)
    }

def generate_trick(concept: str, trick_type: str) -> str:
    try:
        prompts = {
            "acronym": f"Create a meaningful acronym to remember: {concept}.",
            "acrostic": f"Make a sentence where each word starts with letters from: {concept}.",
            "rhymes_songs": f"Write a rhyme to memorize: {concept}.",
            "visualization": f"Describe a visual scene related to: {concept}.",
            "method_of_loci": f"Use the Method of Loci to remember: {concept}.",
            "association": f"Associate {concept} with something daily.",
            "peg_system": f"Use Peg System to link with: {concept}.",
            "key_words_method": f"Create keyword trick for: {concept}."
        }

        prompt = prompts.get(trick_type.lower(), f"Generate a memory trick for: {concept}.")
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(input_ids, max_length=80, num_return_sequences=1, temperature=0.8, top_p=0.9)
        trick = tokenizer.decode(output[0], skip_special_tokens=True).replace(prompt, "").strip()
        return trick

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
