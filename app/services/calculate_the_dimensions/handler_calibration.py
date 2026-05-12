
import cv2
import time
import threading
import statistics
from app.config import PATH_PRODUCT_MODEL,PATH_CONFIG_CALIBRATION
from app.utils import Folder
from app.core import Result,ErrorCode
from app.services.calculate_the_dimensions.handler_model import ModelHandler
from app.services.calculate_the_dimensions.handler_frame_calibration import FrameHandlersCalibration
from app.services.camera import Camera
# from app.utils import obj_queue,name_queue_img_calibration,name_queue_log_client,log_calibration,name_queue_data_client,datatype_Calibration
from app.utils import Tool_OpenCv2
from queue import  Queue


class HandlerCalibration:

    JSON_NAME_CALIBRATION = "calibration"
    JSON_NAME_LINE = "name"
    JSON_NAME_REALITY = "reality"
    JSON_NAME_NUMBER_CPATURE_DETECT = "numberCapture"
    JSON_NAME_DEFAULT_SET ="default"

    VALUE_DEFAULT_CALIBRATION = 0.01
    VALUE_DEFAULT_NUMBER_CPATURE_DETECT = 10
    VALUE_DEFAULT_NAME = "Default"
    VALUE_DEFAUL_REALITY = 10
    IMAGE_WATING_TIMEOUT = 10

    VALUE_TIMEOUT_WAIT_DATA = 20  # chờ timeout giây nếu không nhận được đủ dữ liệu thì thoát thông báo lõi

    def __init__(self,obj_cam:Camera,obj_folder:Folder,obj_opencv:Tool_OpenCv2,queue_log_send_client:Queue,queue_data_send_client:Queue,queue_img_send_client:Queue,type_log,data_calibration):

        self.data_calibration =  data_calibration
        self.queue_log_send_client = queue_log_send_client
        self.queue_data_send_client =  queue_data_send_client
        self.queue_img_send_client = queue_img_send_client
        self.type_log = type_log


        self.obj_cam =  obj_cam
        self.obj_folder = obj_folder
        self.obj_opencv = obj_opencv

        self.name = None
        self.number_capture = 0
        self.reality_length = 0.0
        self.calibration = None
        self.set_deafault = False # ben nay set deafault
        self.Init()

        self.obj_ModelHandler = ModelHandler(PATH_PRODUCT_MODEL)
        self.open_thread_calibration = True
        self._lock = threading.Lock()
        self._complete_work = 0
        self._data_all = {}
    

    def start_run_calibtion(self,line):
        self.thread_task = threading.Thread( target= self.task_work_calibration,args=(line,),daemon = True)
        with self._lock:
            self._data_all = {}
            self._complete_work = 0
        self.thread_task.start()

    @property
    def complete_work(self):
        with self._lock:
            return self._complete_work

    @complete_work.setter
    def complete_work(self, value):
        with self._lock:
            self._complete_work = value

    @property
    def data_all(self):
        with self._lock:
            return self._data_all

    @data_all.setter
    def data_all(self, value):
        with self._lock:
            self._data_all = value

  
    def task_work_calibration(self,line):
        print("---Bắt đầu calibration---")
        if self.obj_cam.get_is_connect():
            number = line.get("numberCapture",self.number_capture)
            reality = line.get("reality",None)
            name =  line.get("name",None)
            for index in range(0,number):
                status,frame = self.obj_cam.capture_once(timeout=1)
                if status:
                    self.queue_img_send_client.put(frame)
            for index in range(0,number):
                #frame = obj_queue.get_timeout(name_queue_img_calibration,HandlerCalibration.IMAGE_WATING_TIMEOUT)
                frame = cv2.imread(r"C:\Users\anhuv\Desktop\test_tool\img_intput\img_5.jpg")
                if frame is None:
                    result = Result.Fail(ErrorCode.CAMERA_TIMEOUT) 
                    self.queue_log_send_client.put({"type":self.type_log,"message":result.message()})
                    continue
                self.process_multi_thread(index,frame,line)
            start_time = time.time()
            self.queue_log_send_client.put({"type":self.type_log,"message":"Đang tính toán tỷ số calibration.\n"})
            
            while True:
                with self._lock:
                    if self._complete_work >= number:
                        break
                self.queue_log_send_client.put({"type":self.type_log,"message":"."})
                if time.time() - start_time > self.VALUE_TIMEOUT_WAIT_DATA:
                    result = Result.Fail(ErrorCode.CALIBRATION_TIMEOUT)
                    self.queue_log_send_client.put({"type":self.type_log,"message":result.message()})
                    return 
                time.sleep(0.2)
            number_picture_ok = 0 
            arr_value_available = []
            for value in self.data_all.values():
                status = value.get("status", False)
                intersections = value.get("intersections", [])
                pixel_length = value.get("pixel_length", 0)
                if status and isinstance(intersections, (list, tuple)) and len(intersections) == 2:
                    arr_value_available.append(pixel_length)
                    number_picture_ok +=1
            result = self.calculate_scale(arr_value_available, self.reality_length)
            if result.ok:
                data = result.data
                self.reality_length = reality
                self.number_capture = number
                self.name  = name
                self.calibration = data.get("scale_mm_per_pixel", 0)
                self.set_deafault = False
                data_new  = self.to_dict()
                data_new["picture_ok"] = number_picture_ok
                data_new["picture_ng"] = number - number_picture_ok
                data_new["pixel_mean"] = data.get("pixel_mean", 0)
                data_new["pixel_std"]  =  data.get("pixel_std", 0)
                data_new["cv"] = data.get("cv", 0)
                data_new["scale_error_mm_per_pixel"] = data.get("scale_error_mm_per_pixel", 0)
                self.write_file_config(data_new)
                self.queue_log_send_client.put({"type":self.type_log,"message":"\nCấu hình Calibration thành công !"})
                self.queue_data_send_client.put({"type":self.data_calibration ,"data_table":data_new})
            else:
                self.queue_log_send_client.put(
                    {
                        "type": self.type_log,
                        "message": result.message(),
                    }
                )
                self.queue_data_send_client.put({"type":self.data_calibration ,"data_table":self.get_data_file()})
            self.data_all.clear()
            self.complete_work = 0
            print("Phán định xong")
        else:
            result = Result.Fail(ErrorCode.CAMERA_DISCONNECT)
            self.queue_log_send_client.put({"type":self.type_log,"message":result.message()})

    def process_multi_thread(self,index,img,line):
        """Hàm này dùng để tạo luồng xử lý phán định sản phẩm trong đa luồng."""
        print(f" Mở luồng thứ {index}")
        t = threading.Thread(
            target= self.worker_judget,name=f"judment_calibration_{index}",
            args=(index,img,line),
            daemon=True 
        )
        t.start()     



    def worker_judget(self,index, img,line):
            polygon = self.obj_ModelHandler.get_polygon(img)
            frame = FrameHandlersCalibration(img, polygon, line)
            status,intersections,pixel_length,img= frame.judment_frame()
            with self._lock:
                self._data_all[str(index)] = {
                    "status": status,
                    "intersections": intersections,
                    "pixel_length": pixel_length
                }
                print(f"Phán định xong ảnh thứ {index}")
                self._complete_work += 1
            frame = self.obj_opencv.convert_frame_to_base64(img)
            self.queue_data_send_client.put({"type":self.data_calibration ,"data_img":frame})


    def Init(self):
            data = self.obj_folder.get_or_create_json_by_path_return_data(PATH_CONFIG_CALIBRATION)
            self.calibration = data.get(
                HandlerCalibration.JSON_NAME_CALIBRATION,
                HandlerCalibration.VALUE_DEFAULT_CALIBRATION
            )
            self.name = data.get(
                HandlerCalibration.JSON_NAME_LINE,
                HandlerCalibration.VALUE_DEFAULT_NAME
            )
            self.reality_length = data.get(
                HandlerCalibration.JSON_NAME_REALITY,
                HandlerCalibration.VALUE_DEFAUL_REALITY
            )
            self.number_capture = data.get(
                HandlerCalibration.JSON_NAME_NUMBER_CPATURE_DETECT,
                HandlerCalibration.VALUE_DEFAULT_NUMBER_CPATURE_DETECT
            )
            self.set_deafault = data.get(
                HandlerCalibration.JSON_NAME_DEFAULT_SET,
                True
            )
            if self.set_deafault:
                self.write_file_config(self.to_dict())
                print("Đây là lần đầu chạy dữ liệu cấu hình Calibrate để phép đo chính xác hơn.")

    def get_data_file(self):
        return self.obj_folder.get_or_create_json_by_path_return_data(PATH_CONFIG_CALIBRATION)

    def write_file_config(self,data:dict):
        if isinstance(data,dict):
            self.obj_folder.write_json_in_file(PATH_CONFIG_CALIBRATION,data)
        else:
            print("Dữ liệu không hợp lệ, phải là dict")
            return False
        return True
    


    def to_dict(self):
        return {
            HandlerCalibration.JSON_NAME_CALIBRATION: self.calibration,
            HandlerCalibration.JSON_NAME_LINE: self.name,
            HandlerCalibration.JSON_NAME_REALITY: self.reality_length,
            HandlerCalibration.JSON_NAME_NUMBER_CPATURE_DETECT: self.number_capture,
            HandlerCalibration.JSON_NAME_DEFAULT_SET: self.set_deafault
        }
    


    def calculate_scale(self, pixel_list, reality_length, outlier_threshold=0.05):
        if len(pixel_list) == 0:
            return Result.Fail(ErrorCode.CALIBRATION_EMPTY_DATA)
        if len(pixel_list) < 2:
            return Result.Fail(ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE)

        median_pixel = statistics.median(pixel_list)

        filtered = [
            p for p in pixel_list
            if abs(p - median_pixel) / median_pixel <= outlier_threshold
        ]

        if len(filtered) < 2:
            return Result.Fail(ErrorCode.CALIBRATION_FILTERED_TOO_MUCH)

        pixel_mean = statistics.mean(filtered)
        pixel_std = statistics.pstdev(filtered)

        if pixel_mean == 0:
            return Result.Fail(ErrorCode.CALIBRATION_MEDIAN_ZERO)

        scale = reality_length / pixel_mean
        scale_std = (pixel_std / pixel_mean) * scale
        cv = pixel_std / pixel_mean

        data = {
            "pixel_mean": pixel_mean,
            "pixel_std": pixel_std,
            "cv": cv,
            "scale_mm_per_pixel": scale,
            "scale_error_mm_per_pixel": scale_std,
            "samples": len(filtered)
        }
        return Result.Ok(data)
    




# import cv2
# cam =  Camera()
# f1 =  Folder()
# H1 = HandlerCalibration(cam,f1)
# data = {                "numberCapture":13,   
#                         "reality":13, 
#                         "PointStarX": 506,
#                         "PointStarY": 296,
#                         "PointEndX": 956,
#                         "PointEndY": 735,
#                         "name": "Duong1"} 
# for i in range (0,20):
#     img = cv2.imread(r"C:\Users\anhuv\Desktop\test_tool\img_intput\img_2.jpg")
#     obj_queue.put(name_queue_img_calibration,img.copy()) # Sau 10s mà không nhận được ảnh thì cho ảnh lỗi và quay về lại gốc
# H1.start_run_calibtion(data)
# H1.thread_task.join()