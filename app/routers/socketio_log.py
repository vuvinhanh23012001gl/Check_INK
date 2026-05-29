import socketio
import asyncio
from fastapi import Request
from app.container import ServiceContainer
from app.core.dependencies import get_services
from fastapi import APIRouter, Depends
from app.config import TypeSend

NAMESPACE_LOG = "/log"
NAMESPACE_DATA = "/data"



sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

@sio.event(namespace = NAMESPACE_LOG)
async def connect(sid, environ):
    print("Client conected to log", sid)

@sio.event(namespace=NAMESPACE_LOG)
async def disconnect(sid):
    print("Client disconnected to log", sid)

@sio.event(namespace=NAMESPACE_DATA)
async def connect(sid, environ):
    print("Client conected to log", sid)

@sio.event(namespace=NAMESPACE_DATA)
async def disconnect(sid):
    print("Client disconnected to log", sid)


async def log_sender(app):
    """Task chạy nền để tiêu thụ dữ liệu từ queue và gửi qua Socket.io"""
    print("📢 Log Sender Task đã bắt đầu...")
    services: ServiceContainer = app.state.services
    while True:
            await sio.emit("status_camera", {"status":services.obj_camera.get_is_connect()}, namespace = NAMESPACE_DATA)
            await sio.emit("status_com", {"status":services.obj_com_service.is_running_com()}, namespace = NAMESPACE_DATA)
            # print("services.obj_com_service.is_running_com()}",services.obj_com_service.is_running_com())
            # print(services.obj_camera.get_is_connect())
            data_log = services.queue_log_send_client.get()
            if data_log is not None:
                log_type = data_log.get("type",None)
                if log_type == TypeSend.type_log_capture:
                    msg = data_log.get("message","")
                    # print("msg",msg)
                    await sio.emit(TypeSend.type_log_capture, {"msg": msg}, namespace = NAMESPACE_LOG)
            await asyncio.sleep(0.5)
  















    #         if log_type == TypeSend.log_calibration:
    #             msg = data_log.get("message","")
    #             await sio.emit(TypeSend.log_calibration, {"msg": msg}, namespace= NAMESPACE_LOG)
    #         if log_type == TypeSend.log_home:
    #             msg = data_log.get("message","")
    #             await sio.emit(TypeSend.log_home, {"msg": msg}, namespace= NAMESPACE_LOG)

    #     data_send_client = services.queue_data_send_client.get()
    #     if data_send_client is not None:
    #         if  data_send_client.get("type",None) == TypeSend.datatype_Calibration:
    #              await sio.emit(TypeSend.datatype_Calibration, {"data": data_send_client}, namespace= NAMESPACE_DATA)  # Cai nay la anh
    #         if data_send_client.get(TypeSend.datatype_Home,None):
    #             # print("đã vào đây rồi nha cú bes")
    #             # print(data_send_client)
    #             await sio.emit(TypeSend.datatype_Home, {"msg":data_send_client}, namespace = NAMESPACE_DATA)










        # await asyncio.sleep(0.01)

        
# obj_queue.put(name_queue_log_client,{"type":log_calibration,"message":result.message()})
# obj_queue.put(name_queue_log_client,{"type":log_Home,"message":"log gui client"})
# # await sio.emit(log_home, {"msg": "Chỗ này để hiển thi log."}, namespace= NAMESPACE_LOG)
#     await sio.emit(log_home, {"msg": "Chỗ này để hiển thi log."}, namespace= NAMESPACE_LOG)
    # test_send = {"type":type_capture,"message":"Test log CaptureProduct"}
    # obj_queue.put(name_queue_log_client, test_send)

        # # # await sio.emit(data_output_judment, {"msg": "xin chao em"}, namespace= NAMESPACE_DATA)
        # # data_client = obj_queue.get(name_queue_data_client)
        # # if data_client is not None:
        # #     
        # 