from fastapi import APIRouter

router = APIRouter(
    prefix="/camera",
    tags=["Camera"]
)

@router.get("/status")
def camera_status():
    return {"status": "ok"}
