import asyncio
from fastapi import APIRouter,Body,Depends
from app.container import ServiceContainer
from app.core.dependencies import get_services
from pydantic import BaseModel
from app.core import (Result,ErrorCode)
from app.validate import ValidateDimesionalCalibration
from app.config import WIDTH_IMG_CAMERA_CAPTURE,HEIGHT_IMG_CAMERA_CAPTURE

router = APIRouter(
    prefix="/dimesional_calibration",
    tags=["Dimesional_Calibration"]
)
class PointData(BaseModel):
    x: float
    y: float
    z: float
class DataIn(BaseModel):
    data: dict


class CalibrationDeleteData(BaseModel):
    product_id: int
    frame_id: int

@router.get("/")
def header_function(services: ServiceContainer = Depends(get_services)):
    print("Bạn vừa nhấn vào đây")
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("Sản phẩm đang chọn",choose_product_current)
    if not choose_product_current.ok:
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    product_result = services.obj_products_service.get_product_by_id(product_id)
    if not product_result.ok:
        return Result.Fail(product_result.error).to_dict()
    product = product_result.data
    points_result = services.obj_point_service.get_points_by_product_id(product_id)
    result_calibration = services.obj_service_calibration.get_calibration_dict_by_product(product_id)
    return Result.Ok({
        "wid_img":WIDTH_IMG_CAMERA_CAPTURE,"hei_img":HEIGHT_IMG_CAMERA_CAPTURE,
        "product": product,
        "data_point": points_result.data if points_result.ok else [],
        "data_dimesion":result_calibration.data
    }).to_dict()



@router.post("/run_point_define_value")
async def run_point_define_value(data:PointData,services: ServiceContainer = Depends(get_services)):
    print(data)
    x = data.x
    y = data.y
    z = data.z
    print(f"Nhận tọa độ: X={x}, Y={y}, Z={z}")
    if not services.obj_iai_control.can_move_iai("Chạy điểm calibration"):
        return {
            "ok": False,
            "message": "❌ Không cho phép di chuyển: IAI chưa về gốc. Hãy nhấn nút xanh để về gốc trước.",
        }
    if services.obj_manager_serial.is_running():
        if services.obj_iai_service.is_valid_position(x,y,z):
            status_resquest_control_services_arm_move = await asyncio.to_thread(
                services.obj_iai_control.move_to_point, x, y, z
            )
            if status_resquest_control_services_arm_move:
                return {
                    "ok": True,
                    "message": f"✅ Gửi điểm X:{x}, Y:{y}, Z:{z} thành công."
                }
            return {
                "ok": False,
                "message": f"❌ Gửi điểm X:{x}, Y:{y}, Z:{z} thất bại."
            }
        return {
            "ok": False,
            "message": f"⚠️Nhận điểm X:{x}, Y:{y}, Z:{z} nằm ngoài giới hạn trục."
        }
    return {
            "ok": False,
            "message": f"⚠️Cổng COM đang không kết nối.Gửi dữ liệu thất bại."
        }
    


@router.get("/exit")
async def exit():
    return {
        "status": "ok",
        "redirect_url": "/"
}

@router.post("/calculater_calibration")
async def calculater_calibration(data:DataIn,services: ServiceContainer = Depends(get_services)):
    data_receive = data.data
    print("data_receive",data_receive)
    status_check,msg = ValidateDimesionalCalibration.validate_product_data_pure_python(data_receive)
    if status_check:
        print("Validate dữ liệu OK")
        services.obj_unet_calib_search_coordinator.set_data_run(data_receive)
        services.obj_unet_calib_search_coordinator.start_algorithm()
        return {
            "ok": True,
            "message": "Đã bắt đầu tính hệ số calibration.",
        }
    else:
        print("Validate dữ liệu NG",msg)
        return {
            "ok": False,
            "message": str(msg),
        }


@router.post("/delete_calibration")
async def delete_calibration(
    data: CalibrationDeleteData,
    services: ServiceContainer = Depends(get_services),
):
    """Xóa kết quả calibration đã lưu của một frame."""
    result = services.obj_service_calibration.delete_calibration(
        data.product_id,
        data.frame_id,
    )
    return result.to_dict()
    