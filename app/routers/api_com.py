from fastapi import APIRouter,Body, Depends
from app.container import ServiceContainer
from app.core.dependencies import get_services
router = APIRouter(
    prefix="/com",
    tags=["Coms"]
)

@router.post("/")
def open_panel_com(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    pass


