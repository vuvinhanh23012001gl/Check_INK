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
from app.engines.service import WeldMeamunetUnetService
from app.engines.model_AI import ModelUnet


from app.inspection.calib_search_coordinator import CalibSearchCoordinator
from app.model import QueueManager, Worker
from app.repository import (
    CalibrationReponsitory,
    ChooseProductRepository,
    ProductRepository,
    PointRepository,
    JudmentLawProductRepository,
    ProductCountRepository
)
from app.services import (
    CalibrationService,
    ChooseProductService,
    ComService,
    IAIService,
    PointService,
    ProductService,
    JudmentLawProductSevice,
    ProductCountService
)
from app.services.camera import Camera
from app.services.log import Config_SoftWare, Infor_Software
from app.validate import ValidateCaptureProduct

from app.config import (PATH_FILE_UNET_DETECT_WELD_LINE,
                        PATH_FILE_UNET_DETECT_FILM_BORDER_LINE,PATH_FILE_MODEL_YOLO_STRUCTURE,PATH_FILE_MODEL_YOLO_SURFACE,
                        PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER,PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER)

from app.config import YoloSegmentConfig
from app.engines.model_AI import ModelYoloObject,ModelYoloSegment
from app.engines.AI_model_process import FrameModelYoloObject
from app.judger import (
    ArmCoverDetector,
    ArmSensorDetector,
    BorderDetector,
    HoleDetector,
    Judment,
    MeasurementWeldingDetector,
    SemiPermeableMembrane,
    ScratchThePipeDetector,
    SlitDetector,
    WeldSeamAirBubbles,
)
from app.config import YoloDetectObjectConfig,ClassNameObjectStructureDetectConfig,ClassNameModelSurfaceConfig
from app.engines.service import StructureFrameYoloService,BorderFilmUnetService,PermeableMembraneService,SurfaceFrameYoloService,EndChippingPatchCoreService,ForeignObjectPatchCoreService
from app.engines.AI_model_process import FrameModelYoloSegment
from app.core.context import RuntimeState


# from app.services.calculate_the_dimensions.handler_calibration import HandlerCalibration
# from app.services.calculate_the_dimensions.handler_work_detect import HandlerWorkDetect
# from app.services.calculate_the_dimensions.handler_work_detect import ImageQueueTester 
# from app.services.product import ChooseProduct,ProductManager





class EnumMode(Enum):
    MODE_IDLE = auto()
    MODE_PREPOCESS = auto()
    MODE_TRANSFORM = auto()
    MODE_EXPORT = auto()


class ServiceContainer:
    def __init__(self):
        self.runtime_state = RuntimeState()
        self.prepared_product = None
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
        self._mode = EnumMode.MODE_IDLE
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
        from app.machine.iaicontrol import IAIControl
        
        
        self.obj_com_reponsitory = ComRepository()
        self.obj_serial_connect = SerialConnect(self.obj_com_reponsitory)
        self.obj_manager_serial = ManagerSerial(self.obj_serial_connect, self.queue_listen_MCU, self.queue_send_MCU)
        self.obj_com_service = ComService(self.obj_manager_serial)
        self.obj_iai_control = IAIControl(
            self.obj_manager_serial,
            self.obj_iai_config
        )
        self.obj_iai_control.start_thread_handl_request_stm32()

        self.obj_camera = Camera()
        print("✔ Camera init")

        # ---------------------------------------------------------
        # 4. KHỞI TẠO TẦNG REPOSITORIES & SERVICES
        # ---------------------------------------------------------
        # Quản lý Point
        self.obj_point_repository = PointRepository()
        self.obj_point_service = PointService(self.obj_point_repository)
        self.obj_end_chipping_patch_core_service = EndChippingPatchCoreService(
            self.obj_point_service
        )
            
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

        # Quản lý số đếm sản phẩm OK/NG/Tổng
        self.obj_product_count_repository = ProductCountRepository()
        self.obj_product_count_service = ProductCountService(self.obj_product_count_repository)
        print("✔ ProductCountService init")

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
        self.CLASS_STRUCTURE_NAME =  ClassNameObjectStructureDetectConfig # cai nay tham chieu den bien khong thay doi
        self.obj_yolo_structure_config  = YoloDetectObjectConfig(path_model = PATH_FILE_MODEL_YOLO_STRUCTURE)
        self.obj_model_yolo_structure = ModelYoloObject(self.obj_yolo_structure_config)
        self.obj_frame_model_yolo_structure =  FrameModelYoloObject(self.obj_model_yolo_structure )
        self.obj_structure_model_service =    StructureFrameYoloService(self.obj_frame_model_yolo_structure)
        self.obj_arm_sensor_detector = ArmSensorDetector(
            self.obj_frame_model_yolo_structure
        )
        self.obj_arm_cover_detector = ArmCoverDetector(
            self.obj_frame_model_yolo_structure
        )
        self.obj_hole_detector = HoleDetector(self.obj_frame_model_yolo_structure)

   
        self.CLASS_SURFACE_NAME =  ClassNameModelSurfaceConfig # cai nay tham chieu den bien khong thay doi
        self.obj_yolo_surface_config  = YoloDetectObjectConfig(path_model = PATH_FILE_MODEL_YOLO_SURFACE)
        self.obj_model_yolo_surface = ModelYoloObject(self.obj_yolo_surface_config)   
        self.obj_frame_model_yolo_surface = FrameModelYoloObject(self.obj_model_yolo_surface)
        self.obj_surface_model_service = SurfaceFrameYoloService(self.obj_frame_model_yolo_surface)
        self.obj_foreign_object_patch_core_service = ForeignObjectPatchCoreService(
            self.obj_point_service,
            self.obj_model_yolo_surface,
        )
        self.obj_scratch_detector = ScratchThePipeDetector(
            self.obj_frame_model_yolo_surface
        )
        self.obj_weld_seam_air_bubbles_detector = WeldSeamAirBubbles(
            self.obj_frame_model_yolo_surface
        )
 



        # Cai nay tam thoi chua dung den
        self.obj_unet_border_line_cofig= UnetConfig(path = PATH_FILE_UNET_DETECT_FILM_BORDER_LINE)
        self.obj_unet_border_line_model = ModelUnet(self.obj_unet_border_line_cofig)
        self.obj_unet_border_film_service =  BorderFilmUnetService(self.obj_unet_border_line_model)
        self.obj_border_detector = BorderDetector(self.obj_unet_border_line_model)

        
        self.config_permeable_membrane_inner = YoloSegmentConfig(path_model= PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER)
        self.config_permeable_membrane_border =  YoloSegmentConfig(path_model= PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER)
       
        self.model_permeable_membrane_inner  = ModelYoloSegment(self.config_permeable_membrane_inner)  # tien hanh load model luon
        self.model_permeable_membrane_border = ModelYoloSegment(self.config_permeable_membrane_border )  # tien hanh load model luon
        self.obj_frame_segment_inner_permeable_membrane = FrameModelYoloSegment(self.model_permeable_membrane_inner)
        self.obj_frame_segment_border_permeable_membrane = FrameModelYoloSegment(self.model_permeable_membrane_border)
        self.obj_judment_permeable_membrane_service = PermeableMembraneService(self.obj_frame_segment_border_permeable_membrane ,self.obj_frame_segment_inner_permeable_membrane)
        self.obj_membrane_detector = SemiPermeableMembrane(
            self.obj_frame_segment_border_permeable_membrane,
            self.obj_frame_segment_inner_permeable_membrane,
        )
      



        self.obj_unet_config_line_master = UnetCofigAutoDetectLineMaster()
        self.obj_unet_weld_line_config = UnetConfig(path = PATH_FILE_UNET_DETECT_WELD_LINE)
        self.obj_unet_weld_line_model = ModelUnet(self.obj_unet_weld_line_config)
        self.obj_measurement_welding_detector = MeasurementWeldingDetector(
            self.obj_unet_weld_line_model
        )
        self.obj_slit_detector = SlitDetector(self.obj_unet_weld_line_model)
        self.obj_judment = Judment({
            "ArmSensorInspector": self.obj_arm_sensor_detector,
            "ArmCoverInspector": self.obj_arm_cover_detector,
            "BorderFilmInspector": self.obj_border_detector,
            "HoleItemInspector": self.obj_hole_detector,
            "ScratchedPipeItemInspector": self.obj_scratch_detector,
            "SlitWeldInspector": self.obj_slit_detector,
            "AirBubblesItemInspector": self.obj_weld_seam_air_bubbles_detector,
            "MeasurementWeldInspector": self.obj_measurement_welding_detector,
            "MembraneInspector": self.obj_membrane_detector,
        })
        self.obj_deployment_Unet = WeldMeamunetUnetService(
            self.obj_unet_config_line_master,
            self.obj_unet_weld_line_model
        )
        
        self.obj_unet_calib_search_coordinator = CalibSearchCoordinator(
            calibrationService=self.obj_service_calibration,
            camera=self.obj_camera,
            com=self.obj_com_service,
            deloymentUnet=self.obj_deployment_Unet,
            queue_send_log_client= self.queue_log_send_client,
            queue_send_data_client=self.queue_data_send_client,
        )


        # Phần AI detect
        
        
        # ---------------------------------------------------------
        # 6. TỰ ĐỘNG MỞ TRÌNH DUYỆT (UI)
        # ---------------------------------------------------------
        def open_browser():
            webbrowser.open("http://127.0.0.1:8000")
        threading.Thread(target=open_browser).start()
   
        print("..--------------------------------.. init Complete ...----------------------------------.")

    def stop(self) -> None:
        """
        Dừng toàn bộ dịch vụ, giải phóng cổng COM, đóng Camera, ngắt luồng và giải phóng bộ nhớ.
        """
        print("🛑 ....Stopping Service & Releasing Resources....")
        try:
            self.runtime_state.request_stop()
        except Exception as e:
            print(f"[Stop] Lỗi request_stop: {e}")

        if getattr(self, "obj_iai_control", None):
            try:
                self.obj_iai_control.stop_thread_input_handler_stm32()
                self.obj_iai_control.stop_thread_handler_stm32()
            except Exception as e:
                print(f"[Stop] Lỗi dừng IAIControl: {e}")

        if getattr(self, "obj_manager_serial", None):
            try:
                self.obj_manager_serial.stop()
            except Exception as e:
                print(f"[Stop] Lỗi dừng ManagerSerial: {e}")

        if getattr(self, "obj_camera", None):
            try:
                self.obj_camera.release()
            except Exception as e:
                print(f"[Stop] Lỗi giải phóng Camera: {e}")

        try:
            import gc
            gc.collect()
            print("🧹 [Memory] Đã thu gom rác bộ nhớ (gc.collect).")
        except Exception:
            pass

    def send_judgment_log(self, message: str) -> None:
        """Gửi log pipeline tới ô log phán định trên giao diện.

        Input: ``message`` là nội dung log dạng chuỗi.
        Output: không trả về; bản tin được đưa vào queue Socket.IO hiện có.
        Errors: queue worker chịu trách nhiệm xử lý lỗi truyền bản tin.
        """
        self.queue_log_send_client.put({
            "type": "log_Home",
            "message": str(message),
        })

    def set_mode(self, mode: EnumMode):
        with self._lock_mode:
            self._mode = mode

    def get_mode(self) -> EnumMode:
        with self._lock_mode:
            return self._mode


def create_container():
    return ServiceContainer()

