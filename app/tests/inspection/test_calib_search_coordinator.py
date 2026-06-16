
import time
from app.inspection.calib_search_coordinator import CalibSearchCoordinator
from app.model import Calibration
from app.model import QueueManager,Worker
from app.repository import CalibrationReponsitory
from app.services import CalibrationService, PointService
from app.repository import PointRepository
from app.services.camera import Camera
from app.manager.serial import ManagerSerial
from app.manager.serial import SerialConnect
from app.repository import ComRepository
from app.config import PATH_FILE_DATA_CONFIG_COM
import queue
from app.model import Line
from app.services import ComService

import cv2

from app.engines.unet_plus import (
    InferenceUnet,
    DeploymentUnetUnet
)
from app.config import (
    UnetConfig,
    UnetCofigAutoDetectLineMaster
)


unet_config = UnetConfig()
auto_detect_config = UnetCofigAutoDetectLineMaster()
       

infer_unet = InferenceUnet(unet_config)
prediction = DeploymentUnetUnet(
        auto_detect_config,
        infer_unet
)

queue_send_MCU = queue.Queue(maxsize=200)
queue_listen_MCU = queue.Queue(maxsize=200)
obj_com_reponsitory = ComRepository(PATH_FILE_DATA_CONFIG_COM)
obj_serial_connect = SerialConnect(obj_com_reponsitory)
obj_manager_serial = ManagerSerial(obj_serial_connect,queue_listen_MCU,queue_send_MCU)
obj_com_service = ComService(obj_manager_serial)

from app.config import (
    PATH_CONFIG_POINTS,
    PATH_CONFIG_CALIBRATION,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
    BASE_DIR
)

# =========================================
# MOCK OBJECT
# =========================================
queue_manager = QueueManager()
obj_camera = Camera()
q_log_send_client = queue_manager.create_queue(
                name="queue_sendata_img",
                maxsize= 200
        )
queue_data_send_client = Worker(q_log_send_client)

point_repository = PointRepository(
        PATH_CONFIG_POINTS
)

point_service = PointService(
        point_repository,
        PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
        PATH_FOLDER_IMG_COORDINATE_PRODUCT,
        PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
        BASE_DIR
)

calibration_repository = CalibrationReponsitory(
        PATH_CONFIG_CALIBRATION
)

service_calibration = CalibrationService(
    point_service,
    calibration_repository
)






class MockDeploymentUnet:
    pass


# =========================================
# TEST
# =========================================

def print_result(title, result):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    
    calib_search_coordinator = CalibSearchCoordinator(
        calibrationService = service_calibration,
        camera = obj_camera,
        com = obj_com_service,
        deloymentUnet= prediction,
        queue_send_client = queue_data_send_client
    )

 

    # calibration = Calibration()

    # result = coordinator.get_parameters()

    # print_result(
    #     "TEST SET PARAMETERS",
    #     result
    # )

    # # ---------------------------------
    # # Test start_algorithm()
    # # ---------------------------------



    # result = coordinator.start_algorithm()

    # print_result(
    #     "TEST START ALGORITHM",
    #     result
    # )

    # time.sleep(3)

    # # ---------------------------------
    # # Test stop_algorithm()
    # # ---------------------------------
    # coordinator.stop_algorithm()

    # print_result(
    #     "TEST STOP ALGORITHM",
    #     coordinator._is_running
    # )

    # # ---------------------------------
    # # Test start lần 2
    # # ---------------------------------
    # calib_search_coordinator.set_data(20, 20, 30, 2, 0, 100, 150, 500, 580, 10, "Yes----")
 
    result = calib_search_coordinator.start_algorithm()
    # print_result(
    #     "TEST START AGAIN",
    #     result
    # )
    #data = {'1': {'0': {'calculation_parameters': {'lineName': '1', 'realityMM': '11', 'captureCount': '111', 'xStart': 441, 'yStart': 139, 'xEnd': 420, 'yEnd': 318, 'coordinateX': 144, 'coordinateY': 31, 'coordinateZ': 30, 'id_item': 6}}, '1': {'calculation_parameters': {'lineName': '1', 'realityMM': '1', 'captureCount': '111', 'xStart': 593, 'yStart': 175, 'xEnd': 569, 'yEnd': 344, 'coordinateX': 67, 'coordinateY': 34, 'coordinateZ': 30, 'id_item': 6}}}}
    #time.sleep(2)
    # # coordinator.stop_algorithm()
    # print("\nHoàn thành test.")
  
    #python -m app.tests.inspection.test_calib_search_coordinator

   #{'1': {'0': {'calculation_parameters': {'lineName': '1', 'realityMM': 11.0, 'captureCount': 111, 'xStart': 441, 'yStart': 139, 'xEnd': 420, 'yEnd': 318, 'coordinateX': 144, 'coordinateY': 31, 'coordinateZ': 30, 'id_item': 6}}, '1': {'calculation_parameters': {'lineName': '1', 'realityMM': 1.0, 'captureCount': 111, 'xStart': 593, 'yStart': 175, 'xEnd': 569, 'yEnd': 344, 'coordinateX': 67, 'coordinateY': 34, 'coordinateZ': 30, 'id_item': 6}}}}