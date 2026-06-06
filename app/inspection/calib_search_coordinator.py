from app.services import CalibrationService,ComService
from app.services.camera import Camera
from app.engines.unet_plus import DeploymentUnetUnet
import threading
import time
from queue import Queue



class CalibSearchCoordinator:
    """Lớp này dùng để tính toán hệ số calibration cho frame ID trước Khi sử dụng lớp này bắt buộc phải nạp dữ liệu mới frame id mới các dữ liệu để cho tính toán"""
    def __init__(self, calibrationService: CalibrationService, camera: Camera, com:ComService,deloymentUnet:DeploymentUnetUnet,queue_send_client:Queue):
        self.calibrationService = calibrationService
        self.camera = camera
        self.com = com
        self.deloymentUnet =  deloymentUnet
        self.queue_send_client:Queue = queue_send_client

        self._lock = threading.Lock()
        self.x:int= 0
        self.y:int = 0
        self.z:int = 0
        self.length_reality:float = 0
        self.frame_id:int = 0
        self.product_id:int = 0
        self.startX:int = 0
        self.startY:int = 0
        self.endX:int = 0
        self.endY:int = 0
        self.number_capture:int = 0
            

    def start_algorithm(self):
        """
        Khởi chạy thuật toán tìm kiếm calib trong một luồng riêng biệt.
        """
        if self._is_running:
            print("Thuật toán Calib đang chạy rồi, không thể khởi chạy thêm!")
            return False
        self._is_running = True
        self._calib_thread = threading.Thread(
            target=self._run_calibration_loop,
            daemon=True # Cho phép luồng tự giải phóng nếu tắt app chính
        )
        
        self._calib_thread.start()
        print("Đã mở luồng xử lý thuật toán Calib thành công.")
        return True


    def _run_calibration_loop(self):
        """
        Hàm thực thi chính chạy ngầm trong luồng.
        """
        print("Bắt đầu tiến trình lấy ảnh và tính toán Calib...")
        try:
            while self._is_running:
                # Lấy number ảnh sau đó cho qua model
                time.sleep(0.03) # ~ 30 FPS

        except Exception as e:
            print(f"Lỗi xảy ra trong luồng Calib: {str(e)}")
        finally:
            # Đảm bảo cờ luôn được hạ xuống khi luồng kết thúc (kể cả khi lỗi)
            self._is_running = False
            print("Luồng xử lý Calib đã dừng hẳn.")

    def stop_algorithm(self):
        """
        Hàm hỗ trợ dừng luồng từ bên ngoài một cách an toàn
        """
        if self._is_running:
            print("Đang yêu cầu dừng luồng Calib...")
            self._is_running = False
            if self._calib_thread:
                self._calib_thread.join(timeout=2.0) # Chờ tối đa 2s để luồng tự tắt

    def set_parameters(
        self,
        x: int = None,
        y: int = None,
        z: int = None,
        length_reality: float = None,
        frame_id: int = None,
        product_id: int = None,
        startX: int = None,
        startY: int = None,
        endX: int = None,
        endY: int = None,
        number_capture: int = None,
    ):
        """Hàm cập nhật thông số - Đã được khóa bảo vệ an toàn đa luồng."""
        # Sử dụng 'with self._lock' để tự động khóa khi ghi dữ liệu và tự giải phóng khi xong
        with self._lock:
            if x is not None:
                self.x = x
            if y is not None:
                self.y = y
            if z is not None:
                self.z = z
            if length_reality is not None:
                self.length_reality = length_reality
            if frame_id is not None:
                self.frame_id = frame_id
            if product_id is not None:
                self.product_id = product_id
            if startX is not None:
                self.startX = startX
            if startY is not None:
                self.startY = startY
            if endX is not None:
                self.endX = endX
            if endY is not None:
                self.endY = endY
            if number_capture is not None:
                self.number_capture = number_capture


    def get_parameters(self) -> dict:
        """Hàm đọc an toàn thông số hiện tại ra dạng dictionary (Dùng cho API hoặc Luồng khác vẽ UI)"""
        with self._lock:
            return {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "length_reality": self.length_reality,
                "frame_id": self.frame_id,
                "product_id": self.product_id,
                "startX": self.startX,
                "startY": self.startY,
                "endX": self.endX,
                "endY": self.endY,
                "number_capture": self.number_capture,
            }