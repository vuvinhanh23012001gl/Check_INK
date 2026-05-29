# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))
# from app.utils import obj_queue,type_capture,name_queue_log_client
from app.model import Point
from fastapi import APIRouter, WebSocket, Body, Depends
from app.container import ServiceContainer
from app.core.dependencies import get_services,get_services_ws
from app.config import TypeSend
import cv2
import asyncio
from pydantic import BaseModel
from app.core import (Result,ErrorCode)

class PointData(BaseModel):
    x: float
    y: float
    z: float

router = APIRouter(
    prefix="/captureproduct",
    tags=["Captureproduct"]
)


# @router.post("/")
# async def captureproduct_load(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
#     print("--------------Vào UI capture----------------")
#     status = payload.get("status")
#     print("Status:", status)    # UI_Capture
#     choose_product_current = services.obj_choose_product.get_choose_product()
#     if choose_product_current.ok:
#         if 

#         return {"ok": choose_product_current.ok, "message": choose_product_current.message(),"error"}
#     else:
#         product_choose = services.obj_products_service.get_product_by_id(choose_product_current)
#         if product_choose.data:
#             infor_iai = services.obj_iai_config.get_dict()
#             # result = services.obj_products_service.get_arr_path_img_roi_product_by_id(choose_product_current)
#             return {"data_point": services.obj_point_service.get_points_by_product_id(choose_product_current),"status": "ok","infor_iai":infor_iai,"product_choose":product_choose.data}
        

@router.post("/")
async def captureproduct_load(
    services: ServiceContainer = Depends(get_services),
    payload: dict = Body(...)
):
    print("--------------Vào UI capture----------------")
    status = payload.get("status")
    print("Status:", status)
    choose_product_current = services.obj_choose_product.get_choose_product()
    print("choose_product_current",choose_product_current)
    if not choose_product_current.ok:
        return Result.Fail(choose_product_current.error).to_dict()
    product_id = choose_product_current.data
    product_result = services.obj_products_service.get_product_by_id(product_id)
    if not product_result.ok:
        return Result.Fail(product_result.error).to_dict()
    product = product_result.data
    infor_iai = services.obj_iai_config.get_dict()
    points_result = services.obj_point_service.get_points_by_product_id(product_id)
    return Result.Ok({
        "product": product,
        "infor_iai": infor_iai,
        "data_point": points_result.data if points_result.ok else [],
    }).to_dict()



@router.get("/infor_product_and_iai")
def infor_product_and_iai(services: ServiceContainer = Depends(get_services)):
    choose_product_current = services.obj_choose_product.get_choose_product().data
    if choose_product_current != -1:
        infor_iai = services.obj_iai_config.get_dict()
        result_product = services.obj_products_service.get_product_by_id(choose_product_current)
        if result_product.ok:
            return {"ok":True,"infor_iai":infor_iai,"product":result_product.data}
        return {"ok":False,"infor_iai":None,"product":None,"messeage":result_product.message()}
    return {"ok":False,"infor_iai":None,"product":None,"messeage":"Bạn chưa chọn loại sản phẩm.Hãy nhấn \"Chọn loại sản phẩm\""}
    
# @router.post("/capture")
# async def capture(
#     services: ServiceContainer = Depends(get_services),
#     data: dict = Body(...)
# ):
#     print("--------------Chụp ảnh point----------------")
#     try:
#         product_selecting = int(data.get("product_selecting"))
#         id_frame = int(data.get("id_frame"))
#         id_point = int(data.get("id_point"))
#         x = int(data.get("x"))
#         y = int(data.get("y"))
#         z = int(data.get("z"))
#     except Exception:
#         return Result.Fail("INVALID_INPUT").to_dict()
#     result_product = services.obj_choose_product.get_choose_product()
#     if result_product.data != product_selecting:
#         return Result.Fail(result_product.error).to_dict()
#     import numpy as np
#     img = np.random.randint(
#         0, 256,
#         (200, 200, 3),
#         dtype=np.uint8
#     )
#     status_check_point = (
#         services.obj_point_service
#         .is_exists_product_frame_point_id(
#             product_selecting,
#             id_frame,
#             id_point
#         )
#     )
#     if not status_check_point:
#         print("Tạo điểm mới")
#         point = Point(id_point, x, y, z)
#         result_action = services.obj_point_service.add_point(
#             product_selecting,
#             id_frame,
#             point,
#             img
#         )


#     else:
#         print("Update điểm cũ")
#         result_action = services.obj_point_service.update_point(
#             product_selecting,
#             id_frame,
#             id_point,
#             x,
#             y,
#             z,
#             img
#         )

#     if not result_action.ok:
#         return Result.Fail(result_action.error).to_dict()

#     product_result = services.obj_products_service.get_product_by_id(
#         product_selecting
#     )

#     if not product_result.ok:
#         return Result.Fail(product_result.error).to_dict()

#     points_result = (
#         services.obj_point_service
#         .get_points_by_product_id(product_selecting)
#     )

#     if not points_result.ok:
#         return Result.Fail(points_result.error).to_dict()

#     infor_iai = services.obj_iai_config.get_dict()

#     return Result.Ok({
#         "product": product_result.data,
#         "infor_iai": infor_iai,
#         "data_point": points_result.data,
#     }).to_dict()



@router.post("/capture")
async def capture(services: ServiceContainer = Depends(get_services),data: dict = Body(...)):

    print("--------------Chụp ảnh point----------------")
    try:
        product_selecting = int(data.get("product_selecting"))
        id_frame = int(data.get("id_frame"))
        id_point = int(data.get("id_point"))
        x = int(data.get("x"))
        y = int(data.get("y"))
        z = int(data.get("z"))
    except Exception:
        print("Lỗi kiểu đinh dạng gửi vào")
        return {
            "ok": False,
            "error": "INVALID_INPUT",
            "message": "Dữ liệu đầu vào không hợp lệ x y z id frame id_point có thể không phải là int"
        }

    if services.obj_choose_product.get_choose_product().data == product_selecting:
        # se thay ham doi anh
        import numpy as np
        img = np.random.randint(
                    0, 256,
                    (200, 200, 3),
                    dtype=np.uint8
        )
        status_check_point = services.obj_point_service.is_exists_product_frame_point_id(product_selecting,id_frame,id_point)
        product = services.obj_products_service.get_product_by_id(product_selecting)
        infor_iai = services.obj_iai_config.get_dict()
        if not status_check_point:
                point = Point(id_point,x,y,z)
                result_add_point = services.obj_point_service.add_point(product_selecting,id_frame,point,img)
                if result_add_point.ok:
                        print("Tạo điểm mới thành công.")
                        return Result.Ok({
                            "data_point": services.obj_point_service.get_points_by_product_id(product_selecting).data,"infor_iai":infor_iai,"product":product.data
                        }).to_dict()
                print("Tạo điểm mới thất bại")
                return {
                    "ok": False,
                    "error": result_add_point.error,
                    "message": result_add_point.message()
                }
        else:
                print("Update điểm cũ đã tồn tại.")
                result_update  = services.obj_point_service.update_point(product_selecting,id_frame,id_point,x,y,z,img)
                if result_update.ok:
                        print("update điểm cũ thành công.")  
                        return Result.Ok({
                            "data_point": services.obj_point_service.get_points_by_product_id(product_selecting).data,"infor_iai":infor_iai,"product":product.data
                        }).to_dict()
                print("Update điểm cũ thất bại.Hãy kiễm tra lại nguyên nhân lỗi")
                return {
                    "ok": False,
                    "error": result_update.error,
                    "message": result_update.message()
                }


@router.get("/exit")
async def exit():
    return {
        "status": "ok",
        "redirect_url": "/"
}

   




      
@router.post("/run_point")
async def run_point(data: PointData,services: ServiceContainer = Depends(get_services)):
    x = data.x
    y = data.y
    z = data.z
    print(f"Nhận tọa độ: X={x}, Y={y}, Z={z}")
    if services.obj_com_service.is_running_com():
        if services.obj_iai_service.is_valid_position(x,y,z):
            services.obj_com_service.send(x,y,z)
            return {
            "status":True,
            "message": f"✅Gửi điểm X:{x}, Y:{y}, Z:{z} thành công."
            }
        return {
            "status": False,
            "message": f"⚠️Nhận điểm X:{x}, Y:{y}, Z:{z} nằm ngoài giới hạn trục."
        }
    return {
            "status": False,
            "message": f"⚠️Cổng COM đang không kết nối.Gửi dữ liệu thất bại."
        }
    

@router.websocket("/ws")
async def camera_ws(ws: WebSocket,services: ServiceContainer = Depends(get_services_ws)):
    # obj_queue.put(name_queue_log_client,{"type":TypeSend.type_capture,"message":"✅ Cammera đã được kết nối."})
    print("✅ Chuẩn bị mở luồng camera")
    await ws.accept()
    try: 
        while True:
            try:
                if services.obj_camera.image is not None:
                    # print("vao ham nay roi ne2")
                    _, buf = cv2.imencode(
                        ".jpg",
                        services.obj_camera.image,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                    )
                    await ws.send_bytes(buf.tobytes())
                if services.obj_camera.camera_lost:
                            print("Main: reconnect camera")
                            services.obj_camera.release()
                            await asyncio.sleep(1)
                            services.obj_camera.refesh_data()
                            services.obj_camera.init()
                            # services.queue_log_send_client.put({"type":TypeSend.type_log_capture,"message":"✅ Cammera Không được kết nối."}) #Gui duoc binh thuong
                else:
                    await asyncio.sleep(0.01)
            except:
                print("Client disconnected:", e)
                await asyncio.sleep(0.1)
    except Exception as e:
        print("WebSocket error:", e)

