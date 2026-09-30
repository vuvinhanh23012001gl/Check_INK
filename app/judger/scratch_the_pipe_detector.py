import numpy as np
from typing import Tuple
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import ClassNameModelSurfaceConfig
from .base_ai import BaseJudgerAI, JudgmentResult

class ScratchThePipeDetector(BaseJudgerAI):
    INSPECTOR_NAME = "ScratchedPipeItemInspector"

    def __init__(self,scratch_the_pipe_model:FrameModelYoloObject):
        super().__init__()
        self.scratch_the_pipe_model = scratch_the_pipe_model

    def define(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int
    ) -> Tuple[bool, list[str], np.ndarray]:
        """Định nghĩa, đánh giá trạng thái và trả về ảnh trực quan của Scratch The Pipe.
        Hàm này gọi đến logic kiểm tra chuyên biệt của mô hình để xác định xem Scratch The Pipe
        trong vùng ảnh cắt có đạt chuẩn hay gặp các lỗi (thiếu, dư, khuyết biên). 
        Đồng thời trả về bức ảnh đã vẽ bounding box của riêng linh kiện này để phục vụ hiển thị.
        Args:
            img (np.ndarray): Ảnh gốc đầu vào cần kiểm tra (mảng NumPy định dạng BGR/RGB).
            x1 (int): Tọa độ X góc trái trên của vùng kiểm tra (vùng crop).
            y1 (int): Tọa độ Y góc trái trên của vùng kiểm tra (vùng crop).
            x2 (int): Tọa độ X góc phải dưới của vùng kiểm tra (vùng crop).
            y2 (int): Tọa độ Y góc phải dưới của vùng kiểm tra (vùng crop).
        Returns:
            Tuple[bool, list[str], np.ndarray]:
                - bool: Trạng thái đánh giá tổng của Scratch The Pipe (True nếu ĐẠT, False nếu CÓ LỖI).
                - list[str]: Danh sách các chuỗi tin nhắn thông báo lỗi chi tiết phát hiện được, 
                             hoặc thông báo thành công nếu linh kiện đạt chuẩn.
                - np.ndarray: Ảnh kết quả có thể hiện vùng kiểm tra và scratch vi phạm.
        """
        return self.scratch_the_pipe_model.search_negative(
            img,
            x1,
            y1,
            x2,
            y2,
            ClassNameModelSurfaceConfig.SCRATCH,
        )

    def compare(self, standard_data, runtime_data):
        """Kiểm tra vùng ảnh không được xuất hiện Scratch.

        Input: ``standard_data`` phải là ``True`` vì Scratch luôn là lỗi;
            ``runtime_data`` là tuple ``(status, messages, image)`` từ
            ``define``.
        Output: dict chứa trạng thái vùng sạch, messages và ảnh kết quả.
        Errors: ``ValueError`` nếu chuẩn hoặc runtime không đúng cấu trúc.
        """
        if standard_data is not True:
            raise ValueError("standard_data của Scratch phải là True")
        if not isinstance(runtime_data, tuple) or len(runtime_data) != 3:
            raise ValueError("runtime_data phải là tuple (status, messages, image)")
        runtime_clean, messages, image = runtime_data
        if not isinstance(runtime_clean, bool):
            raise ValueError("status trong runtime_data phải là bool")
        if not isinstance(messages, list):
            raise ValueError("messages trong runtime_data phải là list")
        return {
            "scratch_forbidden": True,
            "runtime_clean": runtime_clean,
            "messages": messages,
            "image": image,
        }

    def judge(self, comparison_data):
        """Phán định Scratch: có object là NG, không có object là OK.

        Input: dict kết quả từ ``compare``.
        Output: ``JudgmentResult`` với trạng thái ``OK`` khi vùng sạch và
            ``NG`` khi model phát hiện Scratch.
        Errors: ``ValueError`` nếu thiếu dữ liệu bắt buộc.
        """
        required_keys = {"scratch_forbidden", "runtime_clean", "messages"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu Scratch bắt buộc")
        ok = (
            comparison_data["scratch_forbidden"] is True
            and comparison_data["runtime_clean"] is True
        )
        errors = []
        if not ok:
            errors.append(
                f"[Vết xước ống] NG - \"Vết xước\" - Quy định:\"Không có vết xước\" - Thực tế :\"Có vết xước\""
            )
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"scratch_forbidden": True},
            runtime_data={
                "scratch_found": not comparison_data["runtime_clean"],
                "messages": comparison_data["messages"],
            },
            comparison_data=comparison_data,
            message=(
                "Không có vết xước"
                if comparison_data.get("runtime_clean")
                else "Có vết xước"
            ),
            errors=errors,
        )
    