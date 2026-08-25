from app.engines.AI_model_process import FrameModelYoloObject
import numpy as np
from typing import Tuple
from .base_ai import BaseJudgerAI

class WeldSeamAirBubbles(BaseJudgerAI):
    def __init__(self,model_bubble:FrameModelYoloObject):
        super().__init__()
        self.model_bubble  = model_bubble

        
    def define(self, img: np.ndarray, bounding_box_abnormal: list) -> Tuple[bool, list[str], np.ndarray]:
            """
            Nhận diện và đánh giá các vùng bất thường nằm chạm/giao với đường hàn.
            Thực hiện quét bọt khí (bubble check) trên từng vùng giao cắt.
            Args:
                img (np.ndarray): Ảnh gốc đầu vào.
                polygon_weld: Tọa độ đa giác của đường hàn.
                bounding_box_abnormal: Danh sách các bounding box bất thường phát hiện được.
            Returns:
                Tuple[bool, list[str], np.ndarray]:
                    - bool: True nếu TẤT CẢ các vùng kiểm tra đều sạch (Đạt), False nếu có BẤT KỲ vùng nào lỗi (Lỗi).
                    - list[str]: Danh sách tổng hợp tin nhắn log từ tất cả các vùng kiểm tra.
                    - np.ndarray: Ảnh kết quả cuối cùng (đã được vẽ tất cả các bọt khí/vật thể lỗi nếu có).
            """
            # 1. Lấy danh sách các box chạm hoặc nằm trên đường hà=
            if not bounding_box_abnormal:
                success_msg = "OK: Không có vùng bất thường nào nằm đè lên đường hàn."
                return True, [success_msg], img
            all_messages = []
            is_all_valid = True
            img_output = img.copy()  # Tạo bản sao để vẽ đè kết quả lỗi qua từng vòng lặp
            # 2. Duyệt qua từng box giao cắt để kiểm tra chuyên sâu (Negative Check)
            for idx, box in enumerate(bounding_box_abnormal):
                # Chuyển đổi định dạng tọa độ sang xyxy để crop
                xyxy = self._xywh_to_xyxy(box)
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                # Thêm log tiêu đề cho từng vùng để dễ tracking
                all_messages.append(f"--- Kiểm tra vùng đè hàn #{idx + 1} tại [{x1}, {y1}, {x2}, {y2}] ---")
                # Gọi hàm chuyên trách kiểm tra trống hoàn toàn (Absolute Negative Check)
                status, messages, img_visualized = self.model_bubble.search_all_negative(img_output, x1, y1, x2, y2)
                # Gom lochi tiết của vùng này vào danh sách log tổng
                all_messages.extend(messages)
                # Nếu có bất kỳ vùng nào phát hiện vật thể (status = False) -> Kết quả tổng là lỗi (False)
                if not status:
                    is_all_valid = False
                    # Cập nhật lại ảnh đầu ra chứa các nét vẽ bounding box lỗi từ hàm search_all_negative
                    img_output = img_visualized
            return is_all_valid, all_messages, img_output

    def compare(self, standard_data, runtime_data):
        """So sánh dữ liệu bọt khí chuẩn với dữ liệu runtime."""
        raise NotImplementedError

    def judge(self, comparison_data):
        """Phán định dữ liệu bọt khí thành OK hoặc NG."""
        raise NotImplementedError


    def _xywh_to_xyxy(self, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x, y, w, h = box
        return x, y, x + w, y + h
    
              

