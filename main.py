from fastapi import FastAPI
from routes import tricks, search

app = FastAPI(title="Trick Generator API")

# Include different route modules
app.include_router(tricks.router)
app.include_router(search.router)

@app.get("/")
def home():
    return {"message": "Welcome to the Trick Generator API"}
