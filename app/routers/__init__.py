from .api_config_camera import router as camera_router
from .api_config_software import router as software_router
from .api_product import router as product_router
from .home import router as home_router
from .api_captureproduct import router as captureproduct_router
from .socketio_log import sio,log_sender
from .api_draw_regulations import router as draw_regulations_router
from .api_calibration import router as calibration_router

from .api_com import router as com_router
__all__ = [
    "home_router",
    "camera_router",
    "software_router",
    "product_router",
    "captureproduct_router",
    "socket_log",
    "draw_regulations_router",
    "calibration_router",
    "com_router",
]

