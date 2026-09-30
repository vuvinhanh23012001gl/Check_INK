import numpy as np
from typing import Tuple
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import ClassNameObjectStructureDetectConfig
from .base_ai import BaseJudgerAI, JudgmentResult

class ArmSensorDetector(BaseJudgerAI):
    INSPECTOR_NAME = "ArmSensorInspector"

    def __init__(self,arm_sensor_model:FrameModelYoloObject):
        super().__init__()
        self.arm_sensor_model = arm_sensor_model

    def define(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int
    ) -> Tuple[bool, list[str], np.ndarray, list[dict]]:
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
            Tuple[bool, list[str], np.ndarray, list[dict]]:
                - bool: Trạng thái đánh giá tổng của Arm Sensor (True nếu ĐẠT, False nếu CÓ LỖI).
                - list[str]: Danh sách các chuỗi tin nhắn thông báo lỗi chi tiết phát hiện được, 
                             hoặc thông báo thành công nếu linh kiện đạt chuẩn.
                - np.ndarray: Ảnh kết quả sau xử lý (Ảnh gốc chưa vẽ nếu thiếu linh kiện, hoặc ảnh 
                              đã được vẽ bounding box của Arm Sensor).
                - list[dict]: Danh sách các object Arm Sensor được phát hiện.
        """
        return self.arm_sensor_model.search(img, x1, y1, x2, y2,ClassNameObjectStructureDetectConfig.SENSOR_ARM)

    def compare(self, standard_data, runtime_data):
        """So sánh yêu cầu tồn tại Arm Sensor với output của ``define``.

        Input: ``standard_data`` là bool, True nếu ROI phải có Arm Sensor
            và False nếu ROI phải không có Arm Sensor; ``runtime_data`` là
            output tuple của ``define``: ``(status, messages, image, objects)``.
        Output: dict chứa kỳ vọng, thực tế, số object và dữ liệu runtime.
        Errors: ``ValueError`` nếu chuẩn không phải bool hoặc output model
            không đúng cấu trúc.
        """
        if not isinstance(standard_data, bool):
            raise ValueError("standard_data của Arm Sensor phải là bool")
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
            "image": image,
            "objects": objects,
        }

    def judge(self, comparison_data):
        """Phán định Arm Sensor và trả về đầy đủ dữ liệu OK/NG.

        Input: dict kết quả từ ``compare``.
        Output: ``JudgmentResult`` với trạng thái, dữ liệu chuẩn, runtime,
            dữ liệu so sánh và danh sách lỗi.
        Errors: ``ValueError`` nếu thiếu các khóa so sánh bắt buộc.
        """
        required_keys = {"standard_exists", "runtime_exists", "runtime_count"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu Arm Sensor bắt buộc")
        ok = comparison_data["standard_exists"] == comparison_data["runtime_exists"]
        errors = []
        if not ok:
            quy_dinh = "Có ARM Sensor" if comparison_data["standard_exists"] else "Không có ARM Sensor"
            thuc_te = "Có ARM Sensor" if comparison_data["runtime_exists"] else "Không có ARM Sensor"
            errors.append(
                f"[ARM Sensor] NG - \"ARM Sensor\" - Quy định:\"{quy_dinh}\" - Thực tế :\"{thuc_te}\""
            )
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"exists": comparison_data["standard_exists"]},
            runtime_data={
                "exists": comparison_data["runtime_exists"],
                "count": comparison_data["runtime_count"],
                "image": comparison_data.get("image"),
                "objects": comparison_data.get("objects", []),
            },
            comparison_data=comparison_data,
            message=(
                "Có ARM Sensor"
                if ok
                else "Không có ARM Sensor"
            ),
            errors=errors,
        )
    