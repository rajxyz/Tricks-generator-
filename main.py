from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add current directory to sys.path to ensure routes are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import routers from routes package
from routes.tricks import router as tricks_router
from routes.search import router as search_router
from routes.wiki import router as wiki_router  # NEW: For abbreviation fetch

app = FastAPI(title="Trick Generator API")

# Configure CORS to allow all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your allowed domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tricks_router)
app.include_router(search_router)
app.include_router(wiki_router)  # NEW

@app.get("/")
def home():
    return {"message": "Welcome to the Trick Generator API"}
