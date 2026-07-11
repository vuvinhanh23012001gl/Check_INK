import numpy as np
from typing import Tuple
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import ClassNameObjectTargerDetectConfig

class ScratchThePipeDetector:
    def __init__(self,scratch_the_pipe_model:FrameModelYoloObject):
        self.scratch_the_pipe_model = scratch_the_pipe_model

    def search_negative(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> Tuple[bool, list[str]]: # Ham nau nguoc voi ham search còn cấu trúc vẫn vậy
        """Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của linh kiện Arm Sensor.
        Hàm này gọi đến logic kiểm tra chuyên biệt của mô hình để xác định xem linh kiện 
        Arm Sensor trong vùng ảnh cắt có đạt chuẩn hay gặp các lỗi (thiếu, dư, khuyết biên). 
        Đồng thời trả về bức ảnh đã vẽ bounding box của riêng linh kiện này để phục vụ hiển thị.
        Args:
            img (np.ndarray): Ảnh gốc đầu vào cần kiểm tra (mảng NumPy định dạng BGR/RGB).
            x1 (int): Tọa độ X góc trái trên của vùng kiểm tra (vùng crop).
            y1 (int): Tọa độ Y góc trái trên của vùng kiểm tra (vùng crop).
            x2 (int): Tọa độ X góc phải dưới của vùng kiểm tra (vùng crop).
            y2 (int): Tọa độ Y góc phải dưới của vùng kiểm tra (vùng crop).
        Returns:
            Tuple[bool, list[str], np.ndarray]:
                - bool: Trạng thái đánh giá tổng của Arm Sensor (True nếu ĐẠT, False nếu CÓ LỖI).
                - list[str]: Danh sách các chuỗi tin nhắn thông báo lỗi chi tiết phát hiện được, 
                             hoặc thông báo thành công nếu linh kiện đạt chuẩn.
                - np.ndarray: Ảnh kết quả sau xử lý (Ảnh gốc chưa vẽ nếu thiếu linh kiện, hoặc ảnh 
                              đã được vẽ bounding box của Arm Sensor).
        """
        return self.scratch_the_pipe_model.search(img, x1, y1, x2, y2,ClassNameObjectTargerDetectConfig.PIPE_SCRATCHES)
    