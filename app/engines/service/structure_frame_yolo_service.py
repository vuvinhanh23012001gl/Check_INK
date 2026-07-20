
import numpy as np
from app.engines.AI_model_process import FrameModelYoloObject
from app.core import Result, ErrorCode
from app.utils import Tool_OpenCv2
class StructureFrameYoloService:
    def __init__(self, frame_model: FrameModelYoloObject):
        """Khởi tạo StructureFrameYoloService.
        Args:
            frame_model (FrameModelYoloObject): Đối tượng thực hiện nhận diện YOLO.
        """
        self.frame_model = frame_model


    def get_objects_by_label(
            self,
            image: np.ndarray,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            label: str,
            width_canvas: int
        ) -> Result:
            """Lấy danh sách đối tượng theo label trong vùng kiểm tra sau khi quy đổi tọa độ từ Canvas sang Ảnh thực tế."""
            
            # 1. Lấy kích thước thực tế của ảnh gốc (OpenCV load lên)
            h_img, w_img = image.shape[:2]
            
            # 2. Tính tỷ lệ scale (Tránh chia cho 0 nếu width_canvas truyền vào không hợp lệ)
            if width_canvas <= 0:
                return Result.Fail(ErrorCode.INVALID_INPUT)
                
            scale = w_img / width_canvas
            
            # 3. Quy đổi tọa độ từ Canvas sang tọa độ thực trên ảnh gốc
            real_x1 = int(x1 * scale)
            real_y1 = int(y1 * scale)
            real_x2 = int(x2 * scale)
            real_y2 = int(y2 * scale)
            
            # 4. Giới hạn (Clip) các tọa độ thực tế nằm trong biên của ảnh gốc để tránh lỗi Out of Bounds
            real_x1 = max(0, min(real_x1, w_img - 1))
            real_y1 = max(0, min(real_y1, h_img - 1))
            real_x2 = max(0, min(real_x2, w_img - 1))
            real_y2 = max(0, min(real_y2, h_img - 1))
            
            # 5. Truyền tọa độ đã quy đổi chuẩn xác vào hàm search của mô hình AI
            status, _, img, objects = self.frame_model.search(
                image, 
                real_x1, 
                real_y1, 
                real_x2, 
                real_y2, 
                label
            )
            # Tool_OpenCv2.show_img(img)
            if not status:
                return Result.Fail(ErrorCode.LABEL_NOT_FOUND)
            return Result.Ok(objects)