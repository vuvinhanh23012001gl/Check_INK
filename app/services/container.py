
from app.services.calculate_the_dimensions.handler_calibration import HandlerCalibration
from app.services.calculate_the_dimensions.handler_work_detect import HandlerWorkDetect
from app.services.calculate_the_dimensions.handler_work_detect import ImageQueueTester 
from app.services.camera import Camera
from app.utils import Tool_OpenCv2,Folder
from app.services.product import ChooseProduct,ProductManager
from app.services.log import Infor_Software,Config_SoftWare,Manager_Log
from app.utils import Aggregate,Logic


class ServiceContainer:
    def __init__(self):
        print("...----------------------------------.Init Service...-----------------------------.")
        self.obj_logic = Logic()
        self.obj_folder = Folder()
        print("✔ Folder init")
        self.obj_cv2  = Tool_OpenCv2()
        print("✔ Tool_OpenCv2 init")
        self.obj_camera = Camera()
        print("✔ Camera init")
        self.obj_aggregate = Aggregate()
        print("✔ Aggregate init")
        self.obj_calibration = HandlerCalibration(self.obj_camera,self.obj_folder,self.obj_cv2)
        print("✔ HandlerCalibration init")
        self.obj_manager_product = ProductManager(self.obj_folder, self.obj_cv2)
        print("✔ ProductManager init")
        self.obj_choose_product = ChooseProduct(self.obj_folder)
        print("✔ ChooseProduct init")
        self.obj_detect = HandlerWorkDetect(
            self.obj_folder,
            self.obj_choose_product,
            self.obj_manager_product,
            self.obj_calibration
        )
        print("✔ HandlerWorkDetect init")
        self.obj_infor_software = Infor_Software(self.obj_folder)
        print("✔ Infor_Software init")
        self.obj_config_software = Config_SoftWare(self.obj_folder, self.obj_aggregate)
        print("✔ Config_SoftWare init")
        self.obj_manager_log  = Manager_Log(
            self.obj_folder,
            self.obj_config_software,
            self.obj_choose_product,
            self.obj_manager_product,self.obj_aggregate
        )
        print("✔ Manager_Log init")
        self.obj_img_queue_capture_test = ImageQueueTester(self.obj_detect)
        self.obj_img_queue_capture_test.start()

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