import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
from app.container import create_container
from app.pipeline import Pipeline
from enum import Enum
from app.routers import (
    camera_router,
    software_router,
    product_router,
    home_router,
    captureproduct_router,
    sio,draw_regulations_router,calibration_router,dimesional_calibration_router,master_router,
    log_sender,com_router
)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    print("🚀 Đang khởi tạo tài nguyên...")
    fastapi_app.state.services = create_container()
    pipeline =  Pipeline(fastapi_app.state.services)
    asyncio.create_task(log_sender(fastapi_app))
    yield 
    print("🛑 Đang dọn dẹp tài nguyên...")


def create_app():
    # 🔹 FastAPI gốc
    global fastapi_app
    fastapi_app = FastAPI(title="Width Line Detection",lifespan=lifespan)

    # 🔹 Static
    fastapi_app.mount("/static", StaticFiles(directory="app/static"), name="static")
    fastapi_app.mount("/storage", StaticFiles(directory="app/storage"), name="storage")
    
    # 🔹 Router
    fastapi_app.include_router(home_router)
    fastapi_app.include_router(camera_router)
    fastapi_app.include_router(software_router)
    fastapi_app.include_router(product_router)
    fastapi_app.include_router(captureproduct_router)
    fastapi_app.include_router(draw_regulations_router)
    fastapi_app.include_router(calibration_router)
    fastapi_app.include_router(com_router)
    fastapi_app.include_router(dimesional_calibration_router)
    fastapi_app.include_router(master_router)
    # 🔥 QUAN TRỌNG NHẤT – wrap FastAPI bằng Socket.IO
    return socketio.ASGIApp(sio, fastapi_app)


# 🔥 Uvicorn PHẢI chạy biến này
app = create_app()
