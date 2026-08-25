import numpy as np
from typing import Tuple
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import ClassNameObjectStructureDetectConfig
from .base_ai import BaseJudgerAI, JudgmentResult

class ArmCoverDetector(BaseJudgerAI):
    def __init__(self,arm_cover_model:FrameModelYoloObject):
        super().__init__()
        self.arm_cover_model = arm_cover_model

    def define(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> Tuple[bool, list[str], np.ndarray]:
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
        return self.arm_cover_model.search(img, x1, y1, x2, y2,ClassNameObjectStructureDetectConfig.COVER_ARM)

    def compare(self, standard_data, runtime_data):
        """So sánh yêu cầu tồn tại Cover Arm với output của ``define``.

        Input: ``standard_data`` là bool, True nếu ROI phải có Cover Arm và
            False nếu ROI phải không có Cover Arm; ``runtime_data`` là output
            tuple của ``define``: ``(status, messages, image, objects)``.
        Output: dict chứa kỳ vọng, thực tế, số object và dữ liệu runtime.
        Errors: ``ValueError`` nếu chuẩn không phải bool hoặc output model
            không đúng cấu trúc.
        """
        if not isinstance(standard_data, bool):
            raise ValueError("standard_data của Cover Arm phải là bool")
        if not isinstance(runtime_data, tuple) or len(runtime_data) != 4:
            raise ValueError("runtime_data phải là output tuple của define")
        runtime_status, messages, image, objects = runtime_data
        if not isinstance(objects, list):
            raise ValueError("objects trong runtime_data phải là list")
        return {
            "standard_exists": standard_data,
            "runtime_exists": bool(objects),
            "runtime_count": len(objects),
            "runtime_status": runtime_status,
            "messages": messages,
            "objects": objects,
        }

    def judge(self, comparison_data):
        """Phán định Cover Arm và trả về đầy đủ dữ liệu OK/NG.

        Input: dict kết quả từ ``compare``.
        Output: ``JudgmentResult`` với trạng thái, dữ liệu chuẩn, runtime,
            dữ liệu so sánh và danh sách lỗi.
        Errors: ``ValueError`` nếu thiếu các khóa so sánh bắt buộc.
        """
        required_keys = {"standard_exists", "runtime_exists", "runtime_count"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu Cover Arm bắt buộc")
        ok = comparison_data["standard_exists"] == comparison_data["runtime_exists"]
        errors = [] if ok else [
            "Trạng thái tồn tại Cover Arm không phù hợp cấu hình"
        ]
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"exists": comparison_data["standard_exists"]},
            runtime_data={
                "exists": comparison_data["runtime_exists"],
                "count": comparison_data["runtime_count"],
                "objects": comparison_data.get("objects", []),
            },
            comparison_data=comparison_data,
            message=(
                "Cover Arm đúng theo cấu hình"
                if ok
                else "Cover Arm không đúng theo cấu hình"
            ),
            errors=errors,
        )
    