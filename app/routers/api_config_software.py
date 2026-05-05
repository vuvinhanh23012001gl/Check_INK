from fastapi import APIRouter
router = APIRouter(
    prefix="/software",
    tags=["Software"]
)

@router.get("/version")
def software_version():
    return {"version": "1.0.0"}
