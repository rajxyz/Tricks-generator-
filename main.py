from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# CORS allow sab ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model load
generator = pipeline("text2text-generation", model="google/flan-t5-base")

class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def read_root():
    return {"message": "FLAN-T5 Trick Generator is live!"}

@app.post("/generate_trick/")
def generate_trick(request: TrickRequest):
    try:
        prompts = {
            "acronym": f"Create an acronym for: {request.concept}",
            "acrostic": f"Create an acrostic sentence for: {request.concept}",
            "rhymes_songs": f"Create a rhyme or song to remember: {request.concept}",
            "visualization": f"Describe a visual memory image for: {request.concept}",
            "method_of_loci": f"Use method of loci to remember: {request.concept}",
            "association": f"Associate {request.concept} with something daily.",
            "peg_system": f"Use peg system to memorize: {request.concept}",
            "key_words_method": f"Use keyword method for: {request.concept}",
        }

        trick_type = request.trick_type.lower()
        if trick_type not in prompts:
            raise HTTPException(status_code=400, detail="Invalid trick type.")

        output = generator(prompts[trick_type], max_length=100, do_sample=True)[0]['generated_text']
        
        return {
            "concept": request.concept,
            "trick_type": request.trick_type,
            "trick": output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
