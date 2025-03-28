from fastapi import APIRouter

router = APIRouter()

@router.get("/tricks")
def get_tricks():
    return {"message": "List of tricks"}
