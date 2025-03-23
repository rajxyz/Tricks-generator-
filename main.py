from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load smaller model
model_id = "sshleifer/tiny-gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

class TrickRequest(BaseModel):
    concept: str
    trick_type: str

@app.get("/")
def root():
    return {"message": "Tiny GPT2 Trick Generator is live!"}

@app.post("/generate_trick/")
def generate_trick(request: TrickRequest):
    try:
        prompt = f"Generate a {request.trick_type} for {request.concept}:"
        result = generator(prompt, max_new_tokens=50, do_sample=True)[0]["generated_text"]
        return {"concept": request.concept, "trick_type": request.trick_type, "trick": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
