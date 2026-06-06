from fastapi import APIRouter,Body,Depends
from app.container import ServiceContainer
from app.core.dependencies import get_services
from pydantic import BaseModel
from app.core import (Result,ErrorCode)
router = APIRouter(
    prefix="/dimesional_calibration",
    tags=["Dimesional_Calibration"]
)
class PointData(BaseModel):
    x: float
    y: float
    z: float

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
    return Result.Ok({
        "product": product,
        "data_point": points_result.data if points_result.ok else [],
        "data_dimesion":"",
    }).to_dict()

 
@router.post("/run_point_define_value")
async def run_point_define_value(data:PointData,services: ServiceContainer = Depends(get_services)):
    print(data)
    x = data.x
    y = data.y
    z = data.z
    print(f"Nhận tọa độ: X={x}, Y={y}, Z={z}")
    if services.obj_com_service.get_shake_hands_complete():
        if services.obj_iai_service.is_valid_position(x,y,z):
            if  services.obj_com_service.get_shake_hands_complete():
                status_resquest_control_services_arm_move = services.obj_com_service.send_and_wait(x,y,z)
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
                    "message": f"❌ Quá trình bắt tay chưa thành công."
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
