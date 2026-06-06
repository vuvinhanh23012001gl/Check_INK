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
from app.validate import ValidateCaptureProduct
from app.container import EnumMode
class PointData(BaseModel):
    x: float
    y: float
    z: float

router = APIRouter(
    prefix="/captureproduct",
    tags=["Captureproduct"]
)

@router.post("/run_frame")
async def run_frame(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("vao run frame")
    services.set_mode(EnumMode.MODE_RUN_ONE_FRAME)
    
    # print("Người dùng nhấn Run Frame")
    # frame_id_run =  payload.get("FrameID")
    # product_id =  payload.get("ProductID")
    # print(f"Frame ID RunFrame ProductID:{product_id},FrameID:{frame_id_run}")
    # try:
    #     product_id = int(product_id)
    #     frame_id_run = int(frame_id_run)
    # except Exception:
    #     Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    # result_run_frame = services.obj_point_service.get_xyz_by_product_frame(product_id,frame_id_run).data
    # print(result_run_frame)
    return {
        "name": "Ánh",
        "age": 25
    }

@router.post("/run_product")
async def run_frame(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("Người dùng nhấn Run Product")
    product_id =  payload.get("ProductID")
    print(f"Frame ID RunProduct ProductID:{product_id}")
    try:
        product_id = int(product_id)
    except Exception:
        Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    result_run_product = services.obj_point_service.get_all_xyz_by_product_id(product_id).data
    print(result_run_product)
    return {
        "name": "Ánh",
        "age": 25
    }



@router.post("/erase_item_img")
async def erase_item_img(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("--------------Xóa sản Item Point----------------")
    id_product_selecting_now = payload.get("id_product_selecting_now")
    frame_id =  payload.get("FrameID")
    point_id = payload.get("PointID")
    print(f"Sản phẩm xóa Point :{id_product_selecting_now} Frame ID:{frame_id} Point ID:{point_id}")
    try:
        id_product_selecting_now = int(id_product_selecting_now)
        frame_id = int(frame_id)
        point_id = int(point_id)
    except Exception:
        Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    status_data = ValidateCaptureProduct.validate_erase_item_img(id_product_selecting_now,frame_id,point_id)
    if status_data:
        services.obj_point_service.delete_point(id_product_selecting_now,frame_id,point_id)
        infor_iai = services.obj_iai_config.get_dict()
        product = services.obj_products_service.get_product_by_id(id_product_selecting_now)
        return Result.Ok({
            "data_point": services.obj_point_service.get_points_by_product_id(id_product_selecting_now).data,"infor_iai":infor_iai,"product":product.data
        }).to_dict()


@router.post("/erase_frame")
async def erase_frame(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("--------------Xóa sản Item Point----------------")
    id_product_selecting_now = payload.get("id_product_selecting_now")
    frame_id =  payload.get("FrameID")
    print(f"Sản phẩm xóa Frame :{id_product_selecting_now} Frame ID:{frame_id}")
    try:
        id_product_selecting_now = int(id_product_selecting_now)
        frame_id = int(frame_id)
    except Exception:
        Result.Fail(ErrorCode.INVALID_INPUT).to_dict()
    status_data = ValidateCaptureProduct.validate_erase_frame(id_product_selecting_now,frame_id)
    if status_data:
        services.obj_point_service.delete_frame(id_product_selecting_now,frame_id)
        infor_iai = services.obj_iai_config.get_dict()
        product = services.obj_products_service.get_product_by_id(id_product_selecting_now)
        return Result.Ok({
            "data_point": services.obj_point_service.get_points_by_product_id(id_product_selecting_now).data,"infor_iai":infor_iai,"product":product.data
        }).to_dict()








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
        status_cam,img = services.obj_camera.capture_once(1)
        print("status camera",status_cam)
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

