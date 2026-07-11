import numpy as np
from typing import Tuple
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import ClassNameObjectTargerDetectConfig

class ArmCoverDetector:
    def __init__(self,arm_cover_model:FrameModelYoloObject):
        self.arm_cover_model = arm_cover_model

    def define(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> Tuple[bool, list[str]]:
        """Định nghĩa và đánh giá trạng thái của linh kiện Cover Arm trong vùng chỉ định.
        Hàm này đóng vai trò là một wrapper (hàm bọc) gọi đến logic kiểm tra chuyên biệt 
        của mô hình để xác định xem linh kiện Cover Arm trong vùng ảnh cắt có đạt chuẩn 
        hay gặp các lỗi như thiếu, dư, hoặc bị khuyết hay không.
        Args:
            img (np.ndarray): Ảnh gốc đầu vào cần kiểm tra (mảng NumPy định dạng BGR/RGB).
            x1 (int): Tọa độ X góc trái trên của vùng kiểm tra (vùng crop).
            y1 (int): Tọa độ Y góc trái trên của vùng kiểm tra (vùng crop).
            x2 (int): Tọa độ X góc phải dưới của vùng kiểm tra (vùng crop).
            y2 (int): Tọa độ Y góc phải dưới của vùng kiểm tra (vùng crop).
        Returns:
            Tuple[bool, list[str]]:
                - bool: Trạng thái đánh giá tổng của Cover Arm (True nếu ĐẠT, False nếu CÓ LỖI).
                - list[str]: Danh sách các chuỗi tin nhắn thông báo lỗi chi tiết phát hiện được, 
                             hoặc thông báo thành công nếu linh kiện đạt chuẩn.
                - np.ndarray: Ảnh kết quả sau xử lý. Trả về ảnh gốc chưa vẽ nếu gặp lỗi thiếu linh kiện, 
                                hoặc ảnh đã vẽ bounding box của class mục tiêu cho các trường hợp còn lại.
        """
        return self.arm_cover_model.search(img, x1, y1, x2, y2,ClassNameObjectTargerDetectConfig.COVER_ARM)
    