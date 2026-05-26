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

class PointData(BaseModel):
    x: float
    y: float
    z: float

router = APIRouter(
    prefix="/captureproduct",
    tags=["Captureproduct"]
)




@router.post("/")
async def captureproduct_load(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("--------------Vào UI capture----------------")
    status = payload.get("status")
    print("Status:", status)    # UI_Capture
    choose_product_current = services.obj_choose_product.get_choose_product().data
    if choose_product_current == -1:
        msg = " Hiện tại chưa chọn sản phẩm. Vui lòng chọn sản phẩm trước khi chụp!"
        # print(msg)
        services.queue_log_send_client.put({"type": TypeSend.type_log_capture, "message": msg})
        print("--------------Hết UI capture----------------")
        return {"status": "error", "message": msg}
    else:
        product_choose = services.obj_products_service.get_product_by_id(choose_product_current)
        if product_choose.data:
            infor_iai = services.obj_iai_config.get_dict()
            # result = services.obj_products_service.get_arr_path_img_roi_product_by_id(choose_product_current)
            return {"data_point": services.obj_point_service.get_points_by_product_id(choose_product_current),"status": "ok","infor_iai":infor_iai,"product_choose":product_choose.data}



# print("product_selecting",product_selecting)
# print("id_frame:", id_frame)
# print("id_point:", id_point)
# print("x:", x)
# print("y:", y)
# print("z:", z) 

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
            "message": "Dữ liệu đầu vào không hợp lệ"
        }

    if services.obj_choose_product.get_choose_product().data == product_selecting:
        # se thay ham doi anh
        import numpy as np
        img = np.random.randint(
                    0, 256,
                    (200, 200, 3),
                    dtype=np.uint8
        )
        status_check_point = services.obj_point_service.is_exists_product_and_point_id(product_selecting,id_point)
        product_choose = services.obj_products_service.get_product_by_id(product_selecting)
        infor_iai = services.obj_iai_config.get_dict()
        if not status_check_point:
                point = Point(id_point,x,y,z)
                result_add_point = services.obj_point_service.add_point(product_selecting,id_frame,point,img)
                if result_add_point.ok:
                        print("tạo điểm mới thành công")
                        return {
                            "data_point": services.obj_point_service.get_points_by_product_id(product_selecting),"status": "ok","infor_iai":infor_iai,"product_choose":product_choose.data
                        }
                print("Tạo điểm mới thất bại")
                return {
                    "ok": False,
                    "error": result_add_point.error,
                    "message": result_add_point.message()
                }
        else:
                print("Update điểm cũ đã có")
                result_update  = services.obj_point_service.update_point(product_selecting,id_frame,id_point,x,y,z,img)
                if result_update.ok:
                        print("update điểm cũ thành công.")
                        # return {
                        #     "ok": True,
                        #     "data": result_update.data,
                        #     "message": "Success"
                        #     }
                            
                        return {
                            "data_point": services.obj_point_service.get_points_by_product_id(product_selecting),"status": "ok","infor_iai":infor_iai,"product_choose":product_choose.data
                        }
                print("update điểm cũ thất bại")
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

   



# @router.post("/capture")
# async def capture(
#     services: ServiceContainer = Depends(get_services),
#     status: str = Body(...), 
#     index: int = Body(...), 
#     x: float = Body(...), 
#     y: float = Body(...), 
#     k: float = Body(...)
# ):
   
#     print("--- Nhấn nút chụp ảnh ---")
#     choose_product_current = services.obj_choose_product.get_choose_product_pick()
#     if choose_product_current == -1:
#         msg = "Hiện tại chưa chọn sản phẩm. Vui lòng chọn sản phẩm trước khi chụp!"
#         services.queue_log_send_client({"type": TypeSend.type_capture, "message": msg})
#         return {"status": "error"}
#     else:
#         status,frame =  services.obj_camera.capture_once(timeout=1)
#         if not status :
#             msg = "Lỗi trong quá trình lấy ảnh"
#             services.queue_log_send_client({"type": TypeSend.type_capture, "message": msg})
#             return {"status": "error"}
#         services.obj_products_service.add_point_img_product(choose_product_current,frame)
#         status,arr_path_img = services.obj_products_service.get_arr_path_img_roi_product_by_id(choose_product_current)
#         arr_run_point = services.obj_products_service.get_arr_data_run_point_product_by_id(choose_product_current)
#         infor = services.obj_products_service.get_infor_product(choose_product_current)
#         # print("arr_path_img",arr_path_img,"\n arr_run_point",arr_run_point,"\ninfor",infor)
#         return {"status": "ok","path_arr_img": arr_path_img,"arr_point":arr_run_point,"inf_product":infor}
      
@router.post("/run_point")
async def run_point(data: PointData,services: ServiceContainer = Depends(get_services)):
    x = data.x
    y = data.y
    z = data.z
    print(f"Nhận tọa độ: X={x}, Y={y}, Z={z}")
    if services.obj_iai_service.is_valid_position(x,y,z):
        services.obj_com_service.send(x,y,z)
        return {
        "status":True,
        "message": f"Đã nhận tọa độ ({x}, {y}, {z}) và xử lý không thành công."
        }
    return {
        "status": False,
        "message": f"Đã nhận tọa độ ({x}, {y}, {z}) và xử lý thành công."
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

