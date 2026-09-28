"""Module phán định dị vật (Foreign Object Detector).

Đọc dữ liệu nhận diện từ FramePatchCoreObjectDetector và thực hiện so sánh với
tiêu chuẩn kỹ thuật: Vùng kiểm tra không được phép xuất hiện bất kỳ dị vật nào.
Nếu phát hiện object trong vùng bất thường -> phán định NG.
Nếu không phát hiện object trong vùng bất thường -> phán định OK.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from app.engines.AI_model_process.frame_patch_core_object_detector import (
    FramePatchCoreObjectDetector,
)
from .base_ai import BaseJudgerAI, JudgmentResult


class ForeignObjectDetector(BaseJudgerAI):
    """Lớp phán định dị vật kết hợp giữa PatchCore và YOLO Object.

    Tuân thủ hợp đồng BaseJudgerAI với 3 giai đoạn:
    1. ``define``: Thu thập danh sách đối tượng dị vật phát hiện được và trực quan hóa ảnh.
    2. ``compare``: So sánh dữ liệu thực tế với tiêu chuẩn (kỳ vọng không có dị vật).
    3. ``judge``: Đưa ra kết luận cuối cùng (OK nếu sạch, NG nếu phát hiện dị vật).
    """

    INSPECTOR_NAME = "ForeignObjectInspector"

    def __init__(
        self,
        patchcore_object_detector: Optional[FramePatchCoreObjectDetector] = None,
    ) -> None:
        """Khởi tạo detector phán định dị vật.

        Args:
            patchcore_object_detector (Optional[FramePatchCoreObjectDetector]):
                Instance của FramePatchCoreObjectDetector dùng để chạy inference nếu cần.
        """
        super().__init__()
        self.detector = patchcore_object_detector

    def define(
        self,
        img: np.ndarray,
        x1: int = 0,
        y1: int = 0,
        x2: int = 0,
        y2: int = 0,
        detections: Optional[List[Dict[str, Any]]] = None,
        anomaly_boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> Tuple[bool, List[str], np.ndarray, List[Dict[str, Any]]]:
        """Thu thập dữ liệu dị vật từ FramePatchCoreObjectDetector và vẽ trực quan ảnh.

        Args:
            img (np.ndarray): Ảnh đầu vào dạng mảng NumPy (BGR).
            x1 (int): Tọa độ X góc trên bên trái ROI.
            y1 (int): Tọa độ Y góc trên bên trái ROI.
            x2 (int): Tọa độ X góc dưới bên phải ROI.
            y2 (int): Tọa độ Y góc dưới bên phải ROI.
            detections (Optional[List[Dict[str, Any]]]): Dữ liệu đầu ra đã tính sẵn từ
                FramePatchCoreObjectDetector (nếu được truyền trực tiếp từ workflow trước đó).
            anomaly_boxes (Optional[List[Tuple[int, int, int, int]]]): Danh sách các box
                bất thường của PatchCore nếu đã có sẵn.

        Returns:
            Tuple[bool, List[str], np.ndarray, List[Dict[str, Any]]]:
                - bool: True nếu không có dị vật nào (vùng sạch), False nếu phát hiện dị vật.
                - List[str]: Danh sách thông báo trạng thái hoặc cảnh báo chi tiết.
                - np.ndarray: Ảnh đã được vẽ trực quan các vùng bất thường và bbox dị vật.
                - List[Dict[str, Any]]: Danh sách các đối tượng dị vật phát hiện được.

        Raises:
            ValueError: Nếu ảnh đầu vào rỗng hoặc không có dữ liệu inference khả dụng.
        """
        if img is None or img.size == 0:
            raise ValueError("[LỖI][ForeignObjectDetector] Ảnh đầu vào rỗng hoặc không hợp lệ.")

        detected_objects: List[Dict[str, Any]] = []

        # Ưu tiên tái sử dụng output detections được truyền trực tiếp từ FramePatchCoreObjectDetector
        if detections is not None:
            detected_objects = detections
        elif self.detector is not None:
            # Tự động thực thi inference nếu có detector và chưa có detections sẵn
            w, h = img.shape[1], img.shape[0]
            roi_x1 = max(0, x1)
            roi_y1 = max(0, y1)
            roi_x2 = min(w, x2) if x2 > 0 else w
            roi_y2 = min(h, y2) if y2 > 0 else h

            detected_objects = self.detector.detect_anomaly_objects(
                image=img,
                x1=roi_x1,
                y1=roi_y1,
                x2=roi_x2,
                y2=roi_y2,
                anomaly_boxes=anomaly_boxes,
            )

        # Vẽ trực quan hóa các vùng dị thường và bounding box dị vật lên ảnh
        result_image = self._draw_detections(img, detected_objects)

        # Kiểm tra sơ bộ: Vùng sạch khi không có bất kỳ object dị vật nào
        is_clean = len(detected_objects) == 0
        if is_clean:
            messages = ["Không phát hiện bất kỳ dị vật nào trong vùng kiểm tra."]
        else:
            messages = [
                f"Phát hiện dị vật '{det.get('class_name', 'Unknown')}' "
                f"(độ tin cậy: {float(det.get('confidence', 0.0)):.2f}) "
                f"tại tọa độ {det.get('bbox', {})}"
                for det in detected_objects
            ]

        return is_clean, messages, result_image, detected_objects

    def compare(
        self,
        standard_data: Any,
        runtime_data: Tuple[bool, List[str], np.ndarray, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """So sánh kết quả runtime với tiêu chuẩn kỹ thuật (không có dị vật).

        Args:
            standard_data (Any): Dữ liệu chuẩn quy định. Mặc định là True (yêu cầu vùng sạch).
            runtime_data (Tuple[bool, List[str], np.ndarray, List[Dict[str, Any]]]):
                Dữ liệu trả về từ hàm ``define``.

        Returns:
            Dict[str, Any]: Kết quả so sánh chứa trạng thái kỳ vọng, thực tế và số lượng dị vật.

        Raises:
            ValueError: Nếu runtime_data không đúng cấu trúc tuple 4 phần tử.
        """
        if not isinstance(runtime_data, tuple) or len(runtime_data) != 4:
            raise ValueError(
                "[LỖI][ForeignObjectDetector] runtime_data phải là tuple 4 phần tử từ define()."
            )

        runtime_clean, messages, result_image, detections = runtime_data
        if not isinstance(detections, list):
            raise ValueError(
                "[LỖI][ForeignObjectDetector] detections trong runtime_data phải là danh sách list."
            )

        # Tiêu chuẩn: Vùng kiểm tra bắt buộc phải sạch, không có bất kỳ dị vật nào (max = 0)
        expected_clean = True
        if isinstance(standard_data, dict):
            expected_clean = bool(standard_data.get("clean", True))
        elif isinstance(standard_data, bool):
            expected_clean = standard_data

        return {
            "standard_clean": expected_clean,
            "max_allowed_objects": 0,
            "runtime_clean": runtime_clean,
            "runtime_count": len(detections),
            "messages": messages,
            "image": result_image,
            "detections": detections,
        }

    def judge(self, comparison_data: Dict[str, Any]) -> JudgmentResult:
        """Phán định trạng thái cuối cùng: Phát hiện dị vật -> NG, Không phát hiện -> OK.

        Args:
            comparison_data (Dict[str, Any]): Dữ liệu so sánh từ hàm ``compare``.

        Returns:
            JudgmentResult: Kết quả phán định hoàn chỉnh chứa trạng thái OK/NG, dữ liệu chuẩn và lỗi.

        Raises:
            ValueError: Nếu thiếu các khóa bắt buộc trong comparison_data.
        """
        required_keys = {"standard_clean", "runtime_clean", "runtime_count"}
        if not required_keys.issubset(comparison_data):
            raise ValueError(
                "[LỖI][ForeignObjectDetector] comparison_data thiếu các trường bắt buộc."
            )

        # Phán định cốt lõi: Không có dị vật nào được phát hiện -> OK, có bất kỳ dị vật nào -> NG
        is_ok = (
            comparison_data["standard_clean"] is True
            and comparison_data["runtime_count"] == 0
        )

        if is_ok:
            status = "OK"
            message = "Đạt tiêu chuẩn: Không phát hiện dị vật trong vùng bất thường."
            errors: List[str] = []
        else:
            status = "NG"
            count = comparison_data["runtime_count"]
            message = f"Phát hiện {count} dị vật trong vùng bất thường, phán định NG."
            errors = list(comparison_data.get("messages", []))

        return JudgmentResult(
            ok=is_ok,
            status=status,
            standard_data={
                "foreign_forbidden": True,
                "max_allowed_objects": 0,
            },
            runtime_data={
                "foreign_found": not is_ok,
                "count": comparison_data["runtime_count"],
                "detections": comparison_data.get("detections", []),
                "messages": comparison_data.get("messages", []),
                "image": comparison_data.get("image"),
            },
            comparison_data=comparison_data,
            message=message,
            errors=errors,
        )

    @staticmethod
    def _draw_detections(
        image: np.ndarray,
        detections: List[Dict[str, Any]],
    ) -> np.ndarray:
        """Vẽ các vùng bất thường PatchCore và bounding box của đối tượng YOLO lên ảnh.

        Args:
            image (np.ndarray): Ảnh gốc dạng mảng NumPy (BGR).
            detections (List[Dict[str, Any]]): Danh sách các đối tượng phát hiện được.

        Returns:
            np.ndarray: Bản sao ảnh đã được vẽ trực quan.
        """
        canvas = image.copy()
        for det in detections:
            # 1. Vẽ box vùng bất thường do PatchCore phát hiện (màu cam)
            p_box = det.get("patchcore_box")
            if p_box and len(p_box) == 4:
                px, py, pw, ph = (int(v) for v in p_box)
                cv2.rectangle(canvas, (px, py), (px + pw, py + ph), (255, 140, 0), 2)
                cv2.putText(
                    canvas,
                    "Anomaly Region",
                    (px, max(18, py - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 140, 0),
                    1,
                    cv2.LINE_AA,
                )

            # 2. Vẽ bounding box của YOLO phát hiện dị vật (màu đỏ - phán định NG)
            bbox = det.get("bbox", {})
            if bbox:
                bx1 = int(round(float(bbox.get("x1", 0.0))))
                by1 = int(round(float(bbox.get("y1", 0.0))))
                bx2 = int(round(float(bbox.get("x2", 0.0))))
                by2 = int(round(float(bbox.get("y2", 0.0))))
                class_name = str(det.get("class_name", "object"))
                conf = float(det.get("confidence", 0.0))

                cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
                label = f"NG: {class_name} ({conf:.2f})"
                cv2.putText(
                    canvas,
                    label,
                    (bx1, max(18, by1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )
        return canvas
