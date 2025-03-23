from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

app = FastAPI()

# CORS allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & tokenizer (use_fast=False to fix tokenizer error)
tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-common_gen", use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-common_gen")
generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

# Data structure for input
class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def read_root():
    return {"message": "Creative Trick Generator is live!"}

@app.post("/generate_trick/")
def generate_trick(request: TrickRequest):
    try:
        prompt = f"Generate a creative mnemonic or memory trick using {request.trick_type} for: {request.concept}"
        output = generator(prompt, max_length=80, do_sample=True)[0]['generated_text']
        return {
            "concept": request.concept,
            "trick_type": request.trick_type,
            "trick": output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
