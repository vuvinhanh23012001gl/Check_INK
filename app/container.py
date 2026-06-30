import queue
import threading
import webbrowser
from enum import Enum,auto

from app.config import (
    IAIConfig,
    QueueConfig,
    UnetCofigAutoDetectLineMaster,
    UnetConfig,
)
from app.engines.unet_plus import DeploymentUnetUnet, InferenceUnet
from app.inspection.calib_search_coordinator import CalibSearchCoordinator
from app.model import QueueManager, Worker
from app.repository import (
    CalibrationReponsitory,
    ChooseProductRepository,
    ProductRepository,
    PointRepository,
    JudmentLawProductRepository
)
from app.services import (
    CalibrationService,
    ChooseProductService,
    ComService,
    IAIService,
    PointService,
    ProductService,
    JudmentLawProductSevice
)
from app.services.camera import Camera
from app.services.log import Config_SoftWare, Infor_Software
from app.validate import ValidateCaptureProduct

# from app.services.calculate_the_dimensions.handler_calibration import HandlerCalibration
# from app.services.calculate_the_dimensions.handler_work_detect import HandlerWorkDetect
# from app.services.calculate_the_dimensions.handler_work_detect import ImageQueueTester 
# from app.services.product import ChooseProduct,ProductManager


class EnumMode(Enum):
    MODE_DEAFAULT = auto()
    MODE_JUDGEMENT = auto()
    MODE_RUN_SERVICE = auto()
    MODE_RUN_ONE_FRAME = auto()


class ServiceContainer:
    def __init__(self):
        print("---------------Load config-----------")
        self.obj_iai_config = IAIConfig()
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
        self.queue_manage_log = Worker(q_manage)
        self.queue_send_MCU = queue.Queue(maxsize=QueueConfig.SIZE_QUEUE_DATA_SEND_MCU)
        self.queue_listen_MCU = queue.Queue(maxsize=QueueConfig.SIZE_QUEUE_DATA_LISTEN_MCU)

        # ---------------------------------------------------------
        # 2. CHẾ ĐỘ HOẠT ĐỘNG (MODES) & VALIDATE
        # ---------------------------------------------------------
        self._mode = EnumMode.MODE_DEAFAULT
        self._lock_mode = threading.Lock()
    
        print("...----------------------------------.Init Service...-----------------------------.")
        self.obj_validate_capture_product = ValidateCaptureProduct()
        
        # ---------------------------------------------------------
        # 3. PHẦN CỨNG & KẾT NỐI SERIAL COM
        # ---------------------------------------------------------
        # Viết Cấu hình IAI xử dụng COM kết nối
        from app.manager.serial import ManagerSerial
        from app.manager.serial import SerialConnect
        from app.repository import ComRepository
        
        
        self.obj_com_reponsitory = ComRepository()
        self.obj_serial_connect = SerialConnect(self.obj_com_reponsitory)
        self.obj_manager_serial = ManagerSerial(self.obj_serial_connect, self.queue_listen_MCU, self.queue_send_MCU)
        self.obj_com_service = ComService(self.obj_manager_serial)

        self.obj_camera = Camera()
        print("✔ Camera init")

        # ---------------------------------------------------------
        # 4. KHỞI TẠO TẦNG REPOSITORIES & SERVICES
        # ---------------------------------------------------------
        # Quản lý Point
        self.obj_point_repository = PointRepository()
        self.obj_point_service = PointService(self.obj_point_repository)
            
        # Quản lý dữ liệu law regulations
        self.obj_law_regulation_reponsitory = JudmentLawProductRepository()
        self.obj_law_regulation_service = JudmentLawProductSevice(self.obj_law_regulation_reponsitory)

        

        
       

        # Quản lý Product & ChooseProduct
        self.obj_product_repository = ProductRepository()
        self.obj_products_service = ProductService(self.obj_product_repository)
        print("✔ ProductService init")
        
        self.obj_choose_product_repository = ChooseProductRepository()
        self.obj_choose_product = ChooseProductService(self.obj_choose_product_repository, self.obj_products_service)
        print("✔ ChooseProductService init")

        # HandlerWorkDetect (Commented gốc)
        # self.obj_detect = HandlerWorkDetect(
        #     self.obj_choose_product,
        #     self.obj_products_service,
        #     self.obj_calibration, self.queue_data_send_client,self.queue_process_capture,TypeSend.datatype_Home,PATH_PRODUCT_MODEL
        # )
        # print("✔ HandlerWorkDetect init")

        # Cấu hình phần mềm & Log
        self.obj_infor_software = Infor_Software()
        print("✔ Infor_Software init")
        self.obj_config_software = Config_SoftWare()
        print("✔ Config_SoftWare init")
        
        # self.obj_manager_log  = Manager_Log(
        #     self.obj_config_software,
        #     self.obj_choose_product,
        # )
        # print("✔ Manager_Log init")
        
        # self.obj_img_queue_capture_test = ImageQueueTester(self.obj_detect)
        # self.obj_img_queue_capture_test.start()

        print("-------------------------------------------------------------------------------------")
        
        # Quản lý Calibration
        self.obj_calibration_repository = CalibrationReponsitory()                                            
        print("✔ Calibration Reponsitory init")

        self.obj_service_calibration = CalibrationService(
            self.obj_point_service,
            self.obj_calibration_repository
        )
        print("✔ Calibration Service init")



        # ---------------------------------------------------------
        # 5. KHỞI TẠO CÁC AI ENGINES & COORDINATOR
        # ---------------------------------------------------------
        self.obj_unet_config_line_master = UnetCofigAutoDetectLineMaster()
        self.obj_unet_config = UnetConfig()
        self.obj_infer_unet = InferenceUnet(self.obj_unet_config)
        self.obj_deployment_Unet = DeploymentUnetUnet(
            self.obj_unet_config_line_master,
            self.obj_infer_unet
        )
        
        self.obj_unet_calib_search_coordinator = CalibSearchCoordinator(
            calibrationService=self.obj_service_calibration,
            camera=self.obj_camera,
            com=self.obj_com_service,
            deloymentUnet=self.obj_deployment_Unet,
            queue_send_log_client= self.queue_log_send_client,
            queue_send_data_client=self.queue_data_send_client,
        )

        # ---------------------------------------------------------
        # 6. TỰ ĐỘNG MỞ TRÌNH DUYỆT (UI)
        # ---------------------------------------------------------
        def open_browser():
            webbrowser.open("http://127.0.0.1:8000")
        threading.Thread(target=open_browser).start()
   
        print("..--------------------------------.. init Complete ...----------------------------------.")

    def stop(self):
        print("....Stopping Service....")

    def set_mode(self, mode: EnumMode):
        with self._lock_mode:
            self._mode = mode

    def get_mode(self) -> EnumMode:
        with self._lock_mode:
            return self._mode


def create_container():
    return ServiceContainer()

