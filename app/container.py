
# from app.services.calculate_the_dimensions.handler_calibration import HandlerCalibration
# from app.services.calculate_the_dimensions.handler_work_detect import HandlerWorkDetect
# from app.services.calculate_the_dimensions.handler_work_detect import ImageQueueTester 
from app.services.camera import Camera
# from app.services.product import ChooseProduct,ProductManager
from app.services import ProductService,ChooseProductService,IAIService,ComService,PointService
from app.services.log import Infor_Software,Config_SoftWare,Manager_Log
from app.config import QueueConfig,TypeSend,IAIConfig
from app.model import QueueManager,Worker
from app.repository import ChooseProductRepository,ProductRepository,PointRepository
import queue
from app.validate import ValidateCaptureProduct
from app.config import (
    PATH_CONFIG_POINTS,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
    BASE_DIR, PATH_PRODUCT_MODEL,PATH_FILE_DATA_CONFIG_IAI
)

# COM

class ServiceContainer:
    def __init__(self):

        #Load config
        print("---------------Load config-----------")
        self.obj_iai_config = IAIConfig(PATH_FILE_DATA_CONFIG_IAI)
        self.obj_iai_service = IAIService(self.obj_iai_config)        
        print("---------------Tạo hàng đợi-----------")
        
        self.queue_manager = QueueManager()
        q_log_send_client = self.queue_manager.create_queue(
                name=QueueConfig.name_queue_log_client,
                maxsize=100
        )
        q_data_send_client = self.queue_manager.create_queue(
                name=QueueConfig.ame_queue_data_client,
                maxsize=100
        )
        q_img_send_client = self.queue_manager.create_queue(
                name=QueueConfig.name_queue_img_calibration,
                maxsize=100
        )
        q_process_capture = self.queue_manager.create_queue(
                name=QueueConfig.name_queue_process_capture,
                maxsize=100
        )
        q_manage = self.queue_manager.create_queue(
                name=QueueConfig.name_queue_manage,
                maxsize=100
        )

        self.queue_log_send_client = Worker(q_log_send_client)
        self.queue_data_send_client = Worker(q_data_send_client)
        self.queue_img_send_client = Worker(q_img_send_client)
        self.queue_process_capture = Worker(q_process_capture)
        self.queue_manage_log =  Worker(q_manage)

        self.queue_send_MCU = queue.Queue(maxsize=QueueConfig.SIZE_QUEUE_DATA_SEND_MCU)
        self.queue_listen_MCU = queue.Queue(maxsize=QueueConfig.SIZE_QUEUE_DATA_LISTEN_MCU)

        print("...----------------------------------.Init Service...-----------------------------.")
        #validate
        self.obj_validate_capture_product = ValidateCaptureProduct()
        
        # Viết Cấu hình IAI xử dụng COM kết nối
        from app.manager.serial import ManagerSerial
        from app.manager.serial import SerialConnect
        from app.repository import ComRepository
        from app.config import PATH_FILE_DATA_CONFIG_COM
        self.obj_com_reponsitory = ComRepository(PATH_FILE_DATA_CONFIG_COM)
        self.obj_serial_connect = SerialConnect(self.obj_com_reponsitory)
        self.obj_manager_serial = ManagerSerial(self.obj_serial_connect,self.queue_listen_MCU,self.queue_send_MCU)
        self.obj_com_service = ComService(self.obj_manager_serial)

        self.obj_point_repository = PointRepository(PATH_CONFIG_POINTS)
        self.obj_point_service = PointService(self.obj_point_repository,PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
                                              PATH_FOLDER_IMG_COORDINATE_PRODUCT,PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,BASE_DIR)
        self.obj_camera = Camera()
        print("✔ Camera init")
        # self.obj_calibration = HandlerCalibration(self.obj_camera,
        #                                           self.queue_log_send_client,self.queue_data_send_client,
        #                                           self.queue_img_send_client,TypeSend.log_calibration,TypeSend.datatype_Calibration)
        print("✔ HandlerCalibration init")
        self.obj_product_repository = ProductRepository()
        self.obj_products_service = ProductService( self.obj_product_repository)
        print("✔ ProductService init")
        self.obj_choose_product_repository =  ChooseProductRepository()
        self.obj_choose_product = ChooseProductService(self.obj_choose_product_repository,self.obj_products_service)
        print("✔ ChooseProductService init")
        # self.obj_detect = HandlerWorkDetect(
        #     self.obj_choose_product,
        #     self.obj_products_service,
        #     self.obj_calibration, self.queue_data_send_client,self.queue_process_capture,TypeSend.datatype_Home,PATH_PRODUCT_MODEL
        # )
        print("✔ HandlerWorkDetect init")
        self.obj_infor_software = Infor_Software()
        print("✔ Infor_Software init")
        self.obj_config_software = Config_SoftWare()
        print("✔ Config_SoftWare init")
        # self.obj_manager_log  = Manager_Log(
        #     
        #     self.obj_config_software,
        #     self.obj_choose_product,

        # )
        print("✔ Manager_Log init")
        # self.obj_img_queue_capture_test = ImageQueueTester(self.obj_detect)
        # self.obj_img_queue_capture_test.start()

        import webbrowser
        import threading
        def open_browser():
            webbrowser.open("http://127.0.0.1:8000")
        threading.Thread(target = open_browser).start()
   
        print("..--------------------------------.. init Complete ...----------------------------------.")
    def stop(self):
        print("....Stopping Service....")
        # Viết các hàm thoát ở đây


def create_container():
        return ServiceContainer()


# H1 =  ServiceContainer()