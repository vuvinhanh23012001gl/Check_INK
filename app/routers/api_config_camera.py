from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.dependencies import get_services

router = APIRouter(
    prefix="/camera",
    tags=["Camera"]
)



class CameraConfigUpdate(BaseModel):
    """Payload cho các thông số camera operator được phép chỉnh."""

    model_config = ConfigDict(extra="forbid")

    acquisition_frame_rate: Optional[float] = Field(default=None, gt=0)
    exposure_time: Optional[float] = Field(default=None, ge=0)
    gain: Optional[float] = Field(default=None, ge=0)
    exposure_auto: Optional[str] = None
    trigger_mode: Optional[str] = None
    trigger_selector: Optional[str] = None
    gamma: Optional[float] = Field(default=None, gt=0)
    black_level: Optional[float] = Field(default=None, ge=0)


@router.get("/status")
def camera_status(services=Depends(get_services)):
    """Trả về trạng thái kết nối và cấu hình camera.

    Input: service container từ FastAPI dependency.
    Output: trạng thái camera và cấu hình hiện tại.
    Errors: exception nếu camera chưa được khởi tạo.
    """
    camera = services.obj_camera
    return {
        "status": "ok" if camera.get_is_connect() else "disconnected",
        "camera_lost": camera.camera_lost,
        "config": camera.get_config(),
    }


@router.get("/config")
def get_camera_config(services=Depends(get_services)):
    """Lấy cấu hình camera hiện tại, gồm cả white balance calibration."""
    return services.obj_camera.get_config()


@router.get("/exit")
def exit_camera_config():
    """Xác nhận thoát cấu hình camera và yêu cầu frontend tải lại trang chính.

    Input: không có.
    Output: trạng thái xử lý và URL trang chính.
    Errors: không phát sinh ở tầng router.
    """
    print("[CameraRouter] Camera config exit request received")
    return {"status": "ok", "redirect_url": "/"}


def _payload_values(payload: CameraConfigUpdate):
    """Lấy các giá trị khác None từ payload và báo lỗi nếu payload rỗng.

    Input: payload Pydantic của API camera.
    Output: dictionary field cần xử lý.
    Errors: ``HTTPException`` 400 nếu không có field cập nhật.
    """
    values = payload.model_dump(exclude_none=True)
    if not values:
        raise HTTPException(status_code=400, detail="At least one camera field is required")
    return values


@router.post("/config/apply")
def apply_camera_config(payload: CameraConfigUpdate, services=Depends(get_services)):
    """Áp dụng giá trị hiện tại vào camera nhưng chưa lưu file."""
    try:
        values = _payload_values(payload)
        print(f"[CameraRouter] Apply camera config request: {values}")
        result = services.obj_camera.apply_config_values(values)
        print(f"[CameraRouter] Apply camera config result: {result['apply_result']}")
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/config/save")
def save_camera_config(payload: CameraConfigUpdate, services=Depends(get_services)):
    """Lưu cấu hình hiện tại xuống JSON và áp dụng vào camera."""
    try:
        values = _payload_values(payload)
        print(f"[CameraRouter] Save camera config request: {values}")
        result = services.obj_camera.save_config_values(values)
        print(f"[CameraRouter] Save camera config result: {result['apply_result']}")
        return result
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/config/reset")
def reset_camera_config(services=Depends(get_services)):
    """Khôi phục cấu hình từ file JSON và áp dụng lại vào camera."""
    try:
        return services.obj_camera.reset_config()
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
