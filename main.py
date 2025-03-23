from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

app = FastAPI()

# CORS allow sabke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and tokenizer
model_id = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Input format
class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def root():
    return {"message": "Trick Generator with Phi-2 is live!"}

@app.post("/generate_trick/")
def generate_trick(request: TrickRequest):
    try:
        prompts = {
            "acronym": f"Create a smart acronym for: {request.concept}",
            "acrostic": f"Make an acrostic sentence for: {request.concept}",
            "rhymes_songs": f"Create a funny rhyme or song to remember: {request.concept}",
            "visualization": f"Describe a creative visual memory image for: {request.concept}",
            "method_of_loci": f"Use method of loci to remember: {request.concept}",
            "association": f"Make a real-life association with: {request.concept}",
            "peg_system": f"Use peg system to memorize: {request.concept}",
            "key_words_method": f"Use keywords method for: {request.concept}",
        }

        trick_type = request.trick_type.lower()
        prompt = prompts.get(trick_type)
        if not prompt:
            raise HTTPException(status_code=400, detail="Invalid trick type.")

        output = generator(prompt, max_new_tokens=120, temperature=0.9, do_sample=True)[0]['generated_text']

        return {
            "concept": request.concept,
            "trick_type": request.trick_type,
            "trick": output.strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
