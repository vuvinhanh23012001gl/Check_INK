# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))

from fastapi import APIRouter, WebSocket, Body, Depends
from app.services.container import ServiceContainer
from app.core.dependencies import get_services,get_services_ws
from app.utils import obj_queue,type_capture,name_queue_log_client
import cv2
import asyncio


router = APIRouter(
    prefix="/captureproduct",
    tags=["Captureproduct"]
)

@router.post("/")
async def captureproduct_load(services: ServiceContainer = Depends(get_services),payload: dict = Body(...)):
    print("--------------Vào UI capture----------------")
    status = payload.get("status")
    print("Status:", status)    # UI_Capture
    choose_product_current = services.obj_choose_product.get_choose_product_pick()
    if choose_product_current == -1:
        msg = " Hiện tại chưa chọn sản phẩm. Vui lòng chọn sản phẩm trước khi chụp!"
        print(msg)
        obj_queue.put(name_queue_log_client, {"type": type_capture, "message": msg})
        print("--------------Hết UI capture----------------")
        return {"status": "error", "message": msg}
    else:
        status,arr_path_img = services.obj_manager_product.get_arr_path_img_roi_product_by_id(choose_product_current)
        arr_run_point = services.obj_manager_product.get_arr_data_run_point_product_by_id(choose_product_current)
        infor = services.obj_manager_product.get_infor_product(choose_product_current)
        print("arr_path_img",arr_path_img,"\n arr_run_point",arr_run_point,"\ninfor",infor)
        print("--------------Hết UI capture----------------")
        return {"status": "ok","path_arr_img": arr_path_img,"arr_point":arr_run_point,"inf_product":infor}
    



@router.get("/exit")
async def exit():
    return {
        "status": "ok",
        "redirect_url": "/"
}

   



@router.post("/capture")
async def capture(
    services: ServiceContainer = Depends(get_services),
    status: str = Body(...), 
    index: int = Body(...), 
    x: float = Body(...), 
    y: float = Body(...), 
    k: float = Body(...)
):
   
    print("--- Nhấn nút chụp ảnh ---")
    choose_product_current = services.obj_choose_product.get_choose_product_pick()
    if choose_product_current == -1:
        msg = "Hiện tại chưa chọn sản phẩm. Vui lòng chọn sản phẩm trước khi chụp!"
        obj_queue.put(name_queue_log_client, {"type": type_capture, "message": msg})
        return {"status": "error"}
    else:
        status,frame =  services.obj_camera.capture_once(timeout=1)
        if not status :
            msg = "Lỗi trong quá trình lấy ảnh"
            obj_queue.put(name_queue_log_client, {"type": type_capture, "message": msg})
            return {"status": "error"}
        services.obj_manager_product.add_point_img_product(choose_product_current,frame)
        status,arr_path_img = services.obj_manager_product.get_arr_path_img_roi_product_by_id(choose_product_current)
        arr_run_point = services.obj_manager_product.get_arr_data_run_point_product_by_id(choose_product_current)
        infor = services.obj_manager_product.get_infor_product(choose_product_current)
        # print("arr_path_img",arr_path_img,"\n arr_run_point",arr_run_point,"\ninfor",infor)
        return {"status": "ok","path_arr_img": arr_path_img,"arr_point":arr_run_point,"inf_product":infor}
      




@router.websocket("/ws")
async def camera_ws(ws: WebSocket,services: ServiceContainer = Depends(get_services_ws)):
    # obj_queue.put(name_queue_log_client,{"type":type_capture,"message":"✅ Cammera đã được kết nối."})
    print("✅ Cammera đã được kết nối.")
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
                            asyncio.sleep(1)
                            services.obj_camera.refesh_data()
                            services.obj_camera.init()
                else:
                    await asyncio.sleep(0.005)
            except:
                print("Client disconnected:", e)
                await asyncio.sleep(0.1)
   
    except Exception as e:
        print("WebSocket error:", e)

