from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tricks, search

app = FastAPI(title="Trick Generator API")

# 🔥 Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Agar sirf ek domain allow karna hai toh yahan frontend URL daalna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include different route modules
app.include_router(tricks.router)
app.include_router(search.router)

@app.get("/")
def home():
    return {"message": "Welcome to the Trick Generator API"}
