from fastapi import APIRouter,Body
from app.container import ServiceContainer
from app.core.dependencies import get_services
from fastapi import APIRouter, Depends
router = APIRouter(
    prefix="/calibration",
    tags=["Calibration"]
)

# @router.get("/")
# def camera_status():
#     return {"status": "ok"}

import cv2
@router.post("/capture")
async def capture(services: ServiceContainer = Depends(get_services)):
    status,frame = services.obj_camera.capture_once(timeout=1)
    if not status :
            return {"status": "error","message":"Không nhận được frame ảnh."}
    img = cv2.imread(r"C:\Users\anhuv\Desktop\test_tool\img_intput\img_5.jpg")
    return {"status": "ok","img":services.obj_cv2.convert_frame_to_base64(img)}
  #  return {"status": "ok","img":services.obj_cv2.convert_frame_to_base64(frame)}


@router.post("/calculator")
async def calculator(services: ServiceContainer = Depends(get_services),data:dict = Body(...)):
    print("Data Nhận được từ clinet ",data)
    line = data.get("line",{})
    check = services.obj_logic.validate_calibration_data(line)
    status = check.get("status",False)
    if not status:
        message = check.get("message",False)
        return {"status":False,"msg":message}
    services.obj_calibration.start_run_calibtion(line)
    return {"status":True}

@router.get("/init_data")
async def init_data(services: ServiceContainer = Depends(get_services)):
    return services.obj_calibration.get_data_file()


@router.get("/exit")
async def exit():
    return {
        "status": "ok",
        "redirect_url": "/"
}

   