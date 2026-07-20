import numpy as np
from typing import Optional
from app.core import Result, ErrorCode
from app.engines.model_AI import ModelUnet

class BorderFilmUnetService:
    def __init__(self, model_unet: ModelUnet):
        """Khởi tạo service với đối tượng ModelUnet."""
        self.model_unet = model_unet

    def extract_border_polygon(
        self, 
        img: np.ndarray, 
        approx_value: float, 
        min_area: Optional[int]
    ) -> Result:
        """Trích xuất đa giác đường biên từ ảnh bằng ModelUnet và trả về đối tượng Result.
        Args:
            img (np.ndarray): Ảnh gốc đầu vào.
            approx_value (float): Hệ số xấp xỉ khoảng cách cho đa giác.
            min_area (int, optional): Diện tích tối thiểu của contour để xử lý.

        Returns:
            Result: Đối tượng Result chứa đa giác (Ok) hoặc mã lỗi (Fail).
        """
        # 1. Kiểm tra ảnh đầu vào hợp lệ (Không None và không rỗng)
        if img is None or img.size == 0:
            return Result.Fail(ErrorCode.IMAGE_INVALID)
            
        # 2. Kiểm tra tham số approx_value hợp lệ (tránh giá trị âm hoặc bằng 0 không hợp lý)
        if approx_value <= 0:
            return Result.Fail(ErrorCode.INVALID_INPUT)
        try:
            # 3. Gọi mô hình Unet để trích xuất đa giác
            polygon = self.model_unet.get_polygon(img, approx_value, min_area)
            
            # 4. Kiểm tra nếu không tìm thấy đa giác hợp lệ theo cấu hình diện tích/ngưỡng
            if polygon is None:
                return Result.Fail(ErrorCode.DATA_NOT_FOUND)
                
            # 5. Trả về kết quả thành công kèm dữ liệu đa giác
            return Result.Ok(polygon)
            
        except Exception as e:
            # Bắt các lỗi ngoại lệ phát sinh trong quá trình infer (nếu có)
            print(f"Error in extract_border_polygon: {str(e)}")
            return Result.Fail(ErrorCode.DATA_INVALID)