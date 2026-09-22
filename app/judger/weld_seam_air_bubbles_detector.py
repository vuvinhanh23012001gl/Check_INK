from app.engines.AI_model_process import FrameModelYoloObject
import numpy as np
from collections.abc import Mapping
from typing import Tuple
from app.config import ClassNameModelSurfaceConfig
from .base_ai import BaseJudgerAI, JudgmentResult

class WeldSeamAirBubbles(BaseJudgerAI):
    INSPECTOR_NAME = "AirBubblesItemInspector"

    def __init__(self,model_bubble:FrameModelYoloObject):
        super().__init__()
        self.model_bubble  = model_bubble

    def define(
        self,
        img: np.ndarray,
        bounding_box_abnormal: list
    ) -> Tuple[bool, list[str], np.ndarray]:
            """
            Quét bọt khí độc lập trên từng vùng cấm đã cấu hình.
            Args:
                img (np.ndarray): Ảnh gốc đầu vào.
                bounding_box_abnormal: Danh sách vùng dạng tuple
                    ``(x, y, width, height)`` hoặc dict có ``xStart``, ``yStart``,
                    ``xEnd``, ``yEnd``.
            Returns:
                Tuple[bool, list[str], np.ndarray]:
                    - bool: True nếu TẤT CẢ các vùng kiểm tra đều sạch (Đạt), False nếu có BẤT KỲ vùng nào lỗi (Lỗi).
                    - list[str]: Danh sách tổng hợp tin nhắn log từ tất cả các vùng kiểm tra.
                    - np.ndarray: Ảnh kết quả cuối cùng (đã được vẽ tất cả các bọt khí/vật thể lỗi nếu có).
            """
            if img is None or img.size == 0:
                raise ValueError("Ảnh đầu vào không được rỗng")
            if not isinstance(bounding_box_abnormal, list):
                raise ValueError("bounding_box_abnormal phải là list")
            if not bounding_box_abnormal:
                success_msg = "OK: Không có vùng kiểm tra bọt khí nào được cấu hình."
                return True, [success_msg], img
            normalized_regions = self._normalize_regions(bounding_box_abnormal)
            all_messages = []
            is_all_valid = True
            img_output = img.copy()  # Tạo bản sao để vẽ đè kết quả lỗi qua từng vòng lặp
            for idx, box in enumerate(normalized_regions):
                xyxy = self._xywh_to_xyxy(box)
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                all_messages.append(f"--- Kiểm tra vùng bọt khí #{idx + 1} tại [{x1}, {y1}, {x2}, {y2}] ---")
                status, messages, img_visualized = self.model_bubble.search_negative(
                    img_output,
                    x1,
                    y1,
                    x2,
                    y2,
                    ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
                )
                all_messages.extend(messages)
                if not status:
                    is_all_valid = False
                    img_output = img_visualized
            return is_all_valid, all_messages, img_output


    def compare(self, standard_data, runtime_data):
        """So sánh luật cấm bọt khí với kết quả quét runtime.

        Input: ``standard_data`` phải là ``True``; ``runtime_data`` là tuple
            ``(status, messages, image)`` từ ``define``.
        Output: dict chứa trạng thái vùng không có bọt khí.
        Errors: ``ValueError`` nếu dữ liệu không đúng cấu trúc.
        """
        if standard_data is not True:
            raise ValueError("standard_data của bọt khí phải là True")
        if not isinstance(runtime_data, tuple) or len(runtime_data) != 3:
            raise ValueError("runtime_data phải là tuple (status, messages, image)")
        runtime_clean, messages, image = runtime_data
        if not isinstance(runtime_clean, bool):
            raise ValueError("status trong runtime_data phải là bool")
        if not isinstance(messages, list):
            raise ValueError("messages trong runtime_data phải là list")
        return {
            "air_bubble_forbidden": True,
            "runtime_clean": runtime_clean,
            "messages": messages,
            "image": image,
        }

    def judge(self, comparison_data):
        """Phán định bọt khí: có bọt khí là NG, không có là OK.

        Input: dict kết quả từ ``compare``.
        Output: ``JudgmentResult`` với trạng thái ``OK`` hoặc ``NG``.
        Errors: ``ValueError`` nếu thiếu dữ liệu bắt buộc.
        """
        required_keys = {"air_bubble_forbidden", "runtime_clean", "messages"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu bọt khí bắt buộc")
        ok = (
            comparison_data["air_bubble_forbidden"] is True
            and comparison_data["runtime_clean"] is True
        )
        errors = [] if ok else ["Phát hiện bọt khí tại vùng đường hàn"]
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"air_bubble_forbidden": True},
            runtime_data={
                "air_bubble_found": not comparison_data["runtime_clean"],
                "messages": comparison_data["messages"],
            },
            comparison_data=comparison_data,
            message=(
                "Không phát hiện bọt khí"
                if ok
                else "Phát hiện bọt khí, kết quả NG"
            ),
            errors=errors,
        )


    def _xywh_to_xyxy(self, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        """Chuyển box dạng (x, y, width, height) sang (x1, y1, x2, y2).

        Input: box gồm bốn số nguyên.
        Output: tuple tọa độ hai góc đối diện.
        Errors: ``ValueError`` nếu box không có đúng bốn phần tử.
        """
        if not isinstance(box, (list, tuple)) or len(box) != 4:
            raise ValueError("bounding box phải có dạng (x, y, width, height)")
        x, y, w, h = box
        return x, y, x + w, y + h

    @staticmethod
    def _normalize_regions(regions: list) -> list[tuple[int, int, int, int]]:
        """Chuẩn hóa danh sách vùng về dạng ``(x, y, width, height)``.

        Input: Danh sách tuple/list xywh hoặc dict tọa độ xStart/yStart/xEnd/yEnd.
        Output: Danh sách vùng hợp lệ dạng tuple số nguyên.
        Errors: ``ValueError`` nếu vùng sai cấu trúc hoặc có kích thước không dương.
        """
        if not isinstance(regions, list):
            raise ValueError("Danh sách vùng kiểm tra phải là list")
        normalized = []
        for region in regions:
            if isinstance(region, Mapping):
                try:
                    x_start = int(region["xStart"])
                    y_start = int(region["yStart"])
                    x_end = int(region["xEnd"])
                    y_end = int(region["yEnd"])
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError("Vùng dict thiếu tọa độ") from error
                x, y = min(x_start, x_end), min(y_start, y_end)
                width, height = abs(x_end - x_start), abs(y_end - y_start)
            else:
                if not isinstance(region, (list, tuple)) or len(region) != 4:
                    raise ValueError("Vùng phải có dạng xywh hoặc dict tọa độ")
                x, y, width, height = (int(value) for value in region)
            if width <= 0 or height <= 0:
                raise ValueError("Kích thước vùng kiểm tra phải lớn hơn 0")
            normalized.append((x, y, width, height))
        return normalized
    
              

