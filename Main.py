from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = FastAPI()

model_name = "gpt2"
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
            "acronym": f"Create a meaningful acronym to remember: {concept}. Ensure it's easy to recall.",
            "acrostic": f"Make a meaningful sentence (Acrostic) where each word starts with letters from: {concept}.",
            "rhymes_songs": f"Write a short, catchy rhyme or song lyrics to memorize: {concept}.",
            "visualization": f"Describe a visual scene that strongly connects with: {concept}.",
            "method_of_loci": f"Use the Method of Loci to link {concept} with a familiar location for easy recall.",
            "association": f"Create a strong association between {concept} and something common in daily life.",
            "peg_system": f"Use the Peg System to remember {concept} by linking it with numbers (1 = Sun, 2 = Shoe, etc.).",
            "key_words_method": f"Generate a Key Words Method trick to help memorize {concept} by linking keywords."
        }

        prompt = prompts.get(trick_type.lower(), f"Generate a memory trick for: {concept}.")
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=0.8, top_p=0.9)
        trick = tokenizer.decode(output[0], skip_special_tokens=True).replace(prompt, "").strip()
        return trick

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
