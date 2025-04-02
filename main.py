from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(file)))  # Ensure 'routes' is accessible

# ✅ Import routers properly
from routes.tricks import router as tricks_router
from routes.search import router as search_router

app = FastAPI(title="Trick Generator API")

# 🔥 Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include Routers
app.include_router(tricks_router)
app.include_router(search_router)

@app.get("/")
def home():
    return {"message": "Welcome to the Trick Generator API"}
