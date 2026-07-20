import numpy as np
from typing import List, Dict, Optional
from app.core import Result, ErrorCode
from app.engines.AI_model_process import FrameModelYoloSegment
from app.utils import Tool_OpenCv2

class PermeableMembraneService:
    def __init__(
        self, 
        border_semi_permeable_membrane: FrameModelYoloSegment, 
        inner_semi_permeable_membrane: FrameModelYoloSegment
    ):
        """Khởi tạo service nhận trực tiếp hai mô hình phân đoạn YOLO."""
        self.border_semi_permeable_membrane = border_semi_permeable_membrane
        self.inner_semi_permeable_membrane = inner_semi_permeable_membrane

    def extract_membrane_polygons(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        canvas_width: int | None = None,
    ) -> Result:
        """
        Trích xuất đa giác của màng bán thấm.

        Args:
            img: Ảnh gốc.
            x1, y1, x2, y2: Tọa độ ROI.
            canvas_width: Chiều rộng Canvas. Nếu truyền vào thì sẽ tự động
                        chuyển tọa độ Canvas sang tọa độ ảnh gốc.
        Returns:
            Result
        """
        # Kiểm tra ảnh
        if img is None or img.size == 0:
            return Result.Fail(ErrorCode.IMAGE_INVALID)

        # Nếu tọa độ lấy từ Canvas thì chuyển sang ảnh gốc
        if canvas_width is not None:
            x1, y1, x2, y2 = Tool_OpenCv2.convert_canvas_to_image(
                x1,
                y1,
                x2,
                y2,
                canvas_width,
                img,
            )

        # Kiểm tra ROI
        if x1 < 0 or y1 < 0 or x2 <= x1 or y2 <= y1:
            return Result.Fail(ErrorCode.INVALID_INPUT)

        try:
            segments_border = self.border_semi_permeable_membrane.get_segments(
                img, x1, y1, x2, y2
            )

            segments_inner = self.inner_semi_permeable_membrane.get_segments(
                img, x1, y1, x2, y2
            )

            poly_border = self.get_first_class_polygon(segments_border)
            poly_inner = self.get_first_class_polygon(segments_inner)

            if poly_border is None or poly_inner is None:
                return Result.Fail(ErrorCode.DATA_NOT_FOUND)

            return Result.Ok({
                "polygon_border": poly_border.tolist(),
                "polygon_inner": poly_inner.tolist(),
            })

        except Exception as e:
            print(f"Error in PermeableMembraneService: {e}")
            return Result.Fail(ErrorCode.DATA_INVALID)


    def get_first_class_polygon(self, segments: List[Dict]) -> Optional[np.ndarray]:
        """Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách
        segmentation results.
        
        Args:
            segments (List[Dict]): Danh sách kết quả, mỗi dict chứa "class_id" và "polygon".

        Returns:
            Optional[np.ndarray]: Mảng numpy shape (N, 2) kiểu np.int32 hoặc None.
        """
        if not segments:
            return None
            
        first_class_id = segments[0]["class_id"]
        for seg in segments:
            if seg["class_id"] == first_class_id:
                return np.array(seg["polygon"], dtype=np.int32)
        return None
    