from fastapi import APIRouter

router = APIRouter()

@router.get("/api/tricks")  # ✅ Correct Path
def get_tricks():
    return {"message": "List of tricks"}
