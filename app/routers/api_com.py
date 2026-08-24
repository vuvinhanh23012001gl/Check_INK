from fastapi import APIRouter,Body, Depends, HTTPException
from pydantic import BaseModel, Field
from app.container import ServiceContainer
from app.core.dependencies import get_services
router = APIRouter(
    prefix="/com",
    tags=["Coms"]
)


class ComConnectionUpdate(BaseModel):
    """Payload cấu hình cổng COM từ giao diện web."""

    port_name: str = Field(min_length=1)
    baudrate: int = Field(gt=0)

@router.post("/")
def open_panel_com(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    """Tương thích endpoint cũ, trả dữ liệu để mở panel COM."""
    return services.obj_com_service.get_configuration_data()


@router.get("/config")
def get_com_config(services: ServiceContainer = Depends(get_services)):
    """Lấy danh sách cổng và cấu hình COM hiện tại."""
    return services.obj_com_service.get_configuration_data()


@router.post("/config")
def update_com_config(
    payload: ComConnectionUpdate,
    services: ServiceContainer = Depends(get_services),
):
    """Cập nhật cổng COM, lưu JSON và mở kết nối mới."""
    try:
        result = services.obj_com_service.configure_connection(
            payload.port_name,
            payload.baudrate,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return result


