import threading
import time
from typing import Dict, Any, List, Optional
import cv2
from app.config import CalibrationConfig
from app.services import CalibrationService, ComService
from app.services.camera import Camera
from app.model import Calibration
from app.engines.unet_plus import DeploymentUnetUnet
from app.model import Worker
from app.config import (TypeSend,TypeDataSendClient)
  
   

class CalibSearchCoordinator:
    """Lớp phối hợp tính toán hệ số calibration cho frame ID trước khi sử dụng.
    Bắt buộc phải nạp dữ liệu mới qua set_data trước khi chạy thuật toán.
    """
    
    VALUE_TIMEOUT_WAIT_DATA: int = 20 
    MAX_NUMBER_THREAD_RUN_TIME: int = CalibrationConfig.MAX_NUMBER_CALIBRATION_METRICS 

    def __init__(
        self, 
        calibrationService: CalibrationService, 
        camera: Camera, 
        com: ComService, 
        deloymentUnet: DeploymentUnetUnet, 
        queue_send_log_client: Worker,queue_send_data_client:Worker
    ) -> None:
        """Khởi tạo tọa độ viên và cấu hình các dịch vụ liên quan.

        Args:
            calibrationService (CalibrationService): Dịch vụ quản lý dữ liệu calibration.
            camera (Camera): Dịch vụ điều khiển và chụp ảnh từ Camera.
            com (ComService): Dịch vụ truyền thông điều khiển cánh tay ARM.
            deloymentUnet (DeploymentUnetUnet): Engine AI xử lý phân đoạn hình ảnh.
            queue_send_client (Worker): Tiến trình/hàng đợi gửi dữ liệu cho client.
        """
        self.calibrationService: CalibrationService = calibrationService
        self.camera: Camera = camera
        self.com: ComService = com
        self.deloymentUnet: DeploymentUnetUnet = deloymentUnet
        self.queue_send_log_client: Worker = queue_send_log_client
        self.queue_send_data_client: Worker = queue_send_data_client

        self._calib_thread: Optional[threading.Thread] = None
        self._lock: threading.Lock = threading.Lock()
        self._semaphore = threading.BoundedSemaphore(CalibSearchCoordinator.MAX_NUMBER_THREAD_RUN_TIME)
        self._complete_work: int = 0
        self._data_all: Dict[str, Any] = {}

        
        self.data_run = {}
    
    def set_data_run(self, data: Dict[str, Any]) -> None:
        """
        Gán hoặc cập nhật toàn bộ cấu trúc dict dữ liệu chạy (data_run).
        """
        if not isinstance(data, dict):
            print("❌ Dữ liệu truyền vào phải là một Dictionary!")
            return
        self.data_run = data
        print("✅ Đã cập nhật data_run thành công.")


    @property
    def data_all(self) -> Dict[str, Any]:
        """Thread-safe getter lấy toàn bộ dữ liệu kết quả phân tích ảnh.

        Returns:
            Dict[str, Any]: Từ điển chứa kết quả valid_cut và length_line_cut của từng ảnh.
        """
        with self._lock:
            return self._data_all

    @data_all.setter
    def data_all(self, value: Dict[str, Any]) -> None:
        """Thread-safe setter thiết lập dữ liệu kết quả phân tích ảnh.

        Args:
            value (Dict[str, Any]): Từ điển dữ liệu mới cần cập nhật.
        """
        with self._lock:
            self._data_all = value

    @property
    def complete_work(self) -> int:
        """Thread-safe getter lấy số lượng ảnh đã xử lý hoàn thành.

        Returns:
            int: Số lượng ảnh đã hoàn thành xử lý.
        """
        with self._lock:
            return self._complete_work

    @complete_work.setter
    def complete_work(self, value: int) -> None:
        """Thread-safe setter cập nhật số lượng ảnh đã xử lý hoàn thành.

        Args:
            value (int): Số lượng ảnh hoàn thành mới.
        """
        with self._lock:
            self._complete_work = value
        
    def start_algorithm(self) -> None:
        """Khởi chạy thuật toán tìm kiếm calib trong một luồng riêng biệt (Non-blocking)."""
        self.complete_work = 0
        self.data_all = {}
        self._calib_thread = threading.Thread(
            target=self._run_calibration_loop,
            daemon=False 
        )
        self._calib_thread.start()


    def _run_calibration_loop(self) -> None:
        """Vòng lặp chính xử lý thuật toán Calibration: Kiểm tra kết nối, điều khiển ARM di chuyển,

        và kích hoạt tiến trình chụp - tính toán tọa độ. Chạy ngầm trong luồng riêng.
        """
        print("-------------------- Mở luồng xử lý thuật toán Calib------------------------------Đ.")
        self.com.set_shake_hands_complete(True)   
        status_hand_camera: bool = self.camera.get_is_connect() 
        status_hand_camera = True
        status_hand_shake: bool = self.com.get_shake_hands_complete() # Nếu chưa bắt tay thì trả gửi log trả về 
        
        if status_hand_camera and status_hand_shake:
            arr_data_analyze_calculation_parameters: List[Dict[str, Any]] = CalibrationService.analyze_data_to_arrays(self.data_run)
            if arr_data_analyze_calculation_parameters:
                number_frame = 0
                for calculation_parameters in arr_data_analyze_calculation_parameters:
                    number_frame+=1
                    # 1. Trích xuất nhanh các ID điều hướng
                    self.obj_calibration = Calibration()
                    product_id = calculation_parameters.get("product_id")
                    frame_id = calculation_parameters.get("frame_id")
                    id_item = calculation_parameters.get("id_item")
                    
                    # 2. Đưa dữ liệu thô vào đối tượng để ép kiểu tự động duy nhất 1 lần
                    scale = 2048 / 1024 
                    # 2. Truyền tham số và nhân tỉ lệ trực tiếp cho các tọa độ pixel
                    self.obj_calibration.set_calculation_parameters(
                        reality_mm=calculation_parameters.get("realityMM"),
                        
                        # Nhân scale cho các tọa độ X và Y
                        startX=int(calculation_parameters.get("xStart") * scale),
                        startY=int(calculation_parameters.get("yStart") * scale),
                        endX=int(calculation_parameters.get("xEnd") * scale),
                        endY=int(calculation_parameters.get("yEnd") * scale),
                        id_tems=id_item,
                        name_item=calculation_parameters.get("lineName"),
                        number_capture=calculation_parameters.get("captureCount")
                    )

                    # Lấy an toàn tọa độ 3D space, mặc định về 0 nếu bị Null/None
                    coord_x = int(calculation_parameters.get('coordinateX', 0) or 0)
                    coord_y = int(calculation_parameters.get('coordinateY', 0) or 0)
                    coord_z = int(calculation_parameters.get('coordinateZ', 0) or 0)

                    # 3. In log trích xuất từ đối tượng Single Source of Truth
                    print("-" * 50)
                    print(f"📌 [PRODUCT ID]: {product_id} | [Frame ID]: {frame_id} | [ITEM ID]: {self.obj_calibration.id_tems}")
                    print("-" * 50)
                    print(f"  ▪️ Tên đường (lineName):      {self.obj_calibration.name_item}")
                    print(f"  ▪️ Kích thước thực tế:        {self.obj_calibration.reality_mm} mm")
                    print(f"  ▪️ Số lần chụp:               {self.obj_calibration.number_capture}")
                    print(f"  ▪️ Điểm bắt đầu (2D):        X = {self.obj_calibration.startX}, Y = {self.obj_calibration.startY}")
                    print(f"  ▪️ Điểm kết thúc (2D):        X = {self.obj_calibration.endX}, Y = {self.obj_calibration.endY}")
                    print(f"  ▪️ Tọa độ không gian (3D):    X = {coord_x}, Y = {coord_y}, Z = {coord_z}")
                    print("-" * 50)

                    # 4. Kiểm tra hệ thống dựa hoàn toàn trên thuộc tính đã chuẩn hóa
                    if self.calibrationService.is_frame_exists_in_system(int(product_id),(frame_id)):
                        if self.calibrationService.check_calibration_data(
                            str(product_id), 
                            str(frame_id), 
                            self.obj_calibration.id_tems,
                            self.obj_calibration.number_capture, 
                            self.obj_calibration.reality_mm,
                            self.obj_calibration.startX, 
                            self.obj_calibration.startY, 
                            self.obj_calibration.endX, 
                            self.obj_calibration.endY
                        ):
                            print("📌 Bỏ điểm do không nhận thấy sự thay đổi")
                            self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"📌 Bỏ Frame {number_frame} do không nhận thấy sự thay đổi"})
                            continue
                            
                        print("📌 Tại vị trí này chưa có dữ liệu") 
                        # Truyền tọa độ đã ép kiểu an toàn
                        self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f""})
                        self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"📌Bắt đầu tính Frame {number_frame}"})
                        status_resquest_control_services_arm_move = self.com.send_and_wait(coord_x, coord_y, coord_z)
                        if status_resquest_control_services_arm_move:
                            print("📌 Nhận đúng tín hiệu mong đợi")
                            self.process_calculate_calibration(product_id,frame_id,
                                self.obj_calibration.number_capture, 
                                self.obj_calibration.reality_mm, 
                                self.obj_calibration.startX, 
                                self.obj_calibration.startY, 
                                self.obj_calibration.endX, 
                                self.obj_calibration.endY,number_frame
                            )
                        else:
                            print("📌 Nhận không đúng dữ liệu ARM")    
                            self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"❌Nhận không đúng dữ liệu ARM"})
                        continue
                    self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"❌Không tìm thấy điểm trên hệ thống."})
                    print("📌 Không tìm thấy điểm trên hệ thống.")

    def process_multi_thread(
            self, index: int, img: Any, xStart: int, yStart: int, Xend: int, Yend: int
        ) -> None:
            """Tạo luồng mới nhưng luồng này sẽ chịu sự kiểm soát số lượng của Semaphore."""
            t = threading.Thread(
                target=self.worker_judget, 
                name=f"worker_{index}",
                args=(index, img, xStart, yStart, Xend, Yend),
                daemon=True 
            )
            t.start()

    def worker_judget(
            self, index: int, img: Any, xStart: int, yStart: int, Xend: int, Yend: int
        ) -> None:
            """Hàm thực thi lõi: Chỉ chạy xử lý UNet khi Semaphore cho phép."""
            with self._semaphore:
                valid_cut, length_line_cut = self.deloymentUnet.get_line_intersection_width(
                    img, xStart, yStart, Xend, Yend
                )
                with self._lock:
                    self._data_all[str(index)] = {
                        "valid_cut": valid_cut,
                        "length_line_cut": length_line_cut
                    }
                    self._complete_work += 1

    def process_calculate_calibration(
        self,product_id,frame_id,
        number_capture: int, 
        reality_length: float, 
        startX: int, 
        startY: int, 
        endX: int, 
        endY: int,number_frame:int
    ) -> None:
        """Quản lý quy trình thu thập chuỗi ảnh, kích hoạt xử lý đa luồng cho từng ảnh,

        chờ đợi kết quả đồng bộ và gọi hàm tính toán tỷ lệ Scale cuối cùng.

        Args:
            number_capture (int): Số lượng ảnh yêu cầu chụp để làm mẫu tính toán.
            reality_length (float): Kích thước thực tế ngoài đời thực (đơn vị: mm).
            startX (int): Tọa độ X bắt đầu của đoạn thẳng tham chiếu trên ảnh.
            startY (int): Tọa độ Y bắt đầu của đoạn thẳng tham chiếu trên ảnh.
            endX (int): Tọa độ X kết thúc của đoạn thẳng tham chiếu trên ảnh.
            endY (int): Tọa độ Y kết thúc của đoạn thẳng tham chiếu trên ảnh.
        """
        time.sleep(0.2)  
        count_capture_ok: int = 0
        arr_img_photographed: List[Any] = []
        self.complete_work = 0   # reset truoc 
        self.data_all = {}
        
        for index_capture in range(0, number_capture):
            # status, img = self.camera.capture_once(timeout=1)
            status: bool = True
            img: Any = cv2.imread(r"C:\Users\anhuv\Desktop\train\img_input\0_copy (24).jpg")
            if status: 
                count_capture_ok += 1
                arr_img_photographed.append(img)                                                                                     
            else:
                print(f"[Showqueue] Chụp ảnh không thành công [{index_capture}/{number_capture}]")                     
        
        print("✅ [Showqueue] Chụp ảnh thành công") if count_capture_ok == number_capture else print("❌ [Showqueue] Chụp ảnh có lỗi")          
        
        length_img_valid: int = len(arr_img_photographed)
        if length_img_valid == 0:
            print("❌ [Showqueue] Không có ảnh nào hợp lệ để xử lý.")
            return
            
        start_time: float = time.time()
        for index in range(0, length_img_valid):
            self.process_multi_thread(index, arr_img_photographed[index], startX, startY, endX, endY)

        while True:
            if self.complete_work >= length_img_valid:
                break
            if time.time() - start_time > CalibSearchCoordinator.VALUE_TIMEOUT_WAIT_DATA:
                print("❌ [Showqueue] Lỗi time out chưa xử lý xong ảnh")
                break
            time.sleep(0.1)  

        number_picture_ok: int = 0 
        arr_value_available: List[Any] = []
        current_data: Dict[str, Any] = self.data_all
        
        for value in current_data.values():
            valid_cut: bool = value.get("valid_cut", False)
            length_line_cut: Any = value.get("length_line_cut", 0)
            if valid_cut:
                arr_value_available.append(length_line_cut)
                number_picture_ok += 1
                print(f"Hoàn thành: {number_picture_ok}\\{number_capture} ảnh")          
                
        print(f"Yêu cầu chụp :{count_capture_ok}. Số ảnh phán định OK {number_picture_ok}")
        len_arr_value_available: int = len(arr_value_available)
        if len_arr_value_available != 0:
            print(f"Lấy {len_arr_value_available} thực hiện phép đo")
            result_calculate_scale: Any = CalibrationService.calculate_calibration_metrics(arr_value_available, reality_length)                                                                                                                 
            if result_calculate_scale.ok:
                raw_data = result_calculate_scale.data
                self.obj_calibration.set_result_parameters(
                    pixel_mean=raw_data.get("pixel_mean"),
                    pixel_std=raw_data.get("pixel_std"),
                    cv=raw_data.get("cv"),
                    scale_mm_per_pixel=raw_data.get("scale_mm_per_pixel"),
                    scale_error_mm_per_pixel=raw_data.get("scale_error_mm_per_pixel"),
                    confidence=raw_data.get("confidence"),
                    samples_used=raw_data.get("samples_used"),
                    samples_raw=raw_data.get("samples_raw"),
                    mad=raw_data.get("mad")
                ) 
                self.calibrationService.add_calibration(int(product_id),int(frame_id),self.obj_calibration)
                print("✅Tính toán dữ liệu Scale thành công")
                # Gui lai data
                result_calibration = self.calibrationService.get_calibration_dict_by_product(int(product_id))
                self.queue_send_data_client.put({"type":TypeDataSendClient.data_calibration_send_client,"data":result_calibration.data})
                self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"✅Tính toán dữ liệu Calibration thành công"})
                return
            else:
                print("message", result_calculate_scale.message())
                self.queue_send_log_client.put({"type":TypeSend.log_calibration,"message":f"❌Tính toán dữ liệu Scale thất bại"})
                print("❌Tính toán dữ liệu Scale thất bại ")
                return
        print("❌Thất bại.Line không cắt đoạn thẳng")

