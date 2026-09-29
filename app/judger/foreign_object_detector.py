import threading
import cv2
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union

from app.engines.AI_model_process.frame_patch_core_object_detector import (
    FramePatchCoreObjectDetector,
)
from app.config.ai_config import FOREIGN_CLASS_NAME_VIETNAMESE_MAP
from .base_ai import BaseJudgerAI, JudgmentResult


class ForeignObjectDetector(BaseJudgerAI):
    """Bộ phán định dị vật (Foreign Object Detector) trên bề mặt sản phẩm.

    Kết hợp mô hình PatchCore để xác định các vùng bất thường và mô hình YOLO Object
    để nhận diện đối tượng dị vật thực sự trong vùng bất thường đó.
    """

    INSPECTOR_NAME = "ForeignObjectInspector"

    def __init__(
        self,
        foreign_object_model: Optional[FramePatchCoreObjectDetector] = None,
        foreign_service: Optional[Any] = None,
    ) -> None:
        """Khởi tạo detector phát hiện dị vật.

        Args:
            foreign_object_model (FramePatchCoreObjectDetector, optional): Instance kết hợp
                giữa PatchCore và YOLO object detector cố định.
            foreign_service (Any, optional): Service nạp động mô hình PatchCore theo
                từng point (product_id, frame_id, item_id).

        Raises:
            TypeError: Nếu cả hai tham số đều None hoặc model truyền vào không hợp lệ.
        """
        super().__init__()
        if foreign_object_model is None and foreign_service is None:
            raise TypeError("foreign_object_model hoặc foreign_service phải được cung cấp")
        if foreign_object_model is not None and not hasattr(
            foreign_object_model, "detect_anomaly_objects_with_heatmap"
        ):
            raise TypeError(
                "foreign_object_model phải có phương thức detect_anomaly_objects_with_heatmap"
            )
        self.foreign_object_model = foreign_object_model
        self.foreign_service = foreign_service

    def define(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        threshold: float = 0.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Trích xuất dữ liệu bất thường và phát hiện dị vật runtime từ ảnh gốc và ROI.

        Gọi ``detect_anomaly_objects_with_heatmap`` để tính điểm số bất thường (score),
        bản đồ nhiệt (heatmap), và nhận diện dị vật (detections) nếu score > threshold.

        Args:
            img (np.ndarray): Mảng ảnh gốc đầu vào (định dạng BGR/RGB).
            x1 (int): Tọa độ X góc trái trên của vùng kiểm tra (ROI).
            y1 (int): Tọa độ Y góc trái trên của vùng kiểm tra (ROI).
            x2 (int): Tọa độ X góc phải dưới của vùng kiểm tra (ROI).
            y2 (int): Tọa độ Y góc phải dưới của vùng kiểm tra (ROI).
            threshold (float, optional): Ngưỡng điểm bất thường dùng để quyết định
                có chạy YOLO hay không. Mặc định là 0.0.
            **kwargs: Các tham số bổ sung như product_id, frame_id, item_id.

        Returns:
            Dict[str, Any]: Dictionary chứa:
                - "score" (float): Điểm bất thường của toàn vùng ảnh ROI.
                - "heatmap" (np.ndarray | None): Bản đồ nhiệt trực quan vùng bất thường.
                - "detections" (List[Dict[str, Any]]): Danh sách các dị vật phát hiện bởi YOLO.
                - "roi" (Dict[str, int]): Tọa độ ROI x1, y1, x2, y2 đã kiểm tra.
                - "threshold_applied" (float): Ngưỡng đã dùng khi define.
                - "image" (np.ndarray): Ảnh gốc (hoặc ảnh có vẽ kết quả khi phát hiện dị vật).

        Raises:
            ValueError: Nếu ảnh rỗng, tọa độ ROI không hợp lệ hoặc thiếu thông tin point.
            RuntimeError: Nếu chưa có model khả dụng.
        """
        if not isinstance(img, np.ndarray) or img.size == 0:
            raise ValueError("img đầu vào không được rỗng")
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Tọa độ ROI không hợp lệ: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        model = self.foreign_object_model
        if model is None and self.foreign_service is not None:
            product_id = kwargs.get("product_id")
            frame_id = kwargs.get("frame_id")
            item_id = kwargs.get("item_id")
            if product_id is None or frame_id is None or item_id is None:
                raise ValueError(
                    f"Thiếu thông tin product_id, frame_id, item_id để nạp mô hình: {kwargs}"
                )
            model = self.foreign_service.get_detector_engine(product_id, frame_id, item_id)
        if model is None:
            raise RuntimeError("Chưa có foreign_object_model để thực thi")

        result = model.detect_anomaly_objects_with_heatmap(
            img, x1, y1, x2, y2, threshold=float(threshold)
        )

        score = float(result.get("score", 0.0))
        heatmap = result.get("heatmap")
        detections: List[Dict[str, Any]] = result.get("detections", [])
        anomaly_boxes: List[Tuple[int, int, int, int]] = result.get("anomaly_boxes", [])

        # Lưu ảnh crop ROI runtime phục vụ train PatchCore nếu cờ saveRuntimeImages được bật
        save_runtime_images = kwargs.get("saveRuntimeImages", False)
        if str(save_runtime_images).lower() == "true":
            p_id = kwargs.get("product_id")
            f_id = kwargs.get("frame_id")
            i_id = kwargs.get("item_id")
            if p_id is not None and f_id is not None and i_id is not None and self.foreign_service is not None:
                roi_img = img[y1:y2, x1:x2].copy()
                threading.Thread(
                    target=self.foreign_service.save_runtime_image_for_training,
                    args=(p_id, f_id, i_id, roi_img),
                    daemon=True,
                ).start()

        # Tạo bản sao ảnh để vẽ kết quả trực quan phục vụ UI
        annotated_image = img.copy()

        # 1. Phủ bản đồ nhiệt PatchCore (heatmap colormap JET) lên toàn bộ vùng ROI kiểm tra
        if heatmap is not None and isinstance(heatmap, np.ndarray) and heatmap.size > 0:
            h_roi, w_roi = y2 - y1, x2 - x1
            if heatmap.shape[:2] == (h_roi, w_roi):
                annotated_image[y1:y2, x1:x2] = heatmap
            else:
                resized_heatmap = cv2.resize(heatmap, (w_roi, h_roi))
                annotated_image[y1:y2, x1:x2] = resized_heatmap

        # 2. Vẽ khung và nhãn các vùng bất thường (heatmap anomaly boxes) phát hiện được
        for idx, abox in enumerate(anomaly_boxes):
            px, py, pw, ph = (int(v) for v in abox)
            # Khung viền màu vàng cam rực rỡ (0, 215, 255), độ dày 2px
            cv2.rectangle(annotated_image, (px, py), (px + pw, py + ph), (0, 215, 255), 2)
            label_anom = f"Vung loi #{idx + 1}"
            (tw, th), _ = cv2.getTextSize(label_anom, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            bg_y1 = max(0, py - th - 6)
            cv2.rectangle(annotated_image, (px, bg_y1), (px + tw + 6, py), (0, 215, 255), -1)
            cv2.putText(
                annotated_image,
                label_anom,
                (px + 3, py - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        # 3. Vẽ đối tượng dị vật phát hiện bởi YOLO bên trong các vùng heatmap bất thường
        if detections:
            for det in detections:
                bbox = det.get("bbox", {})
                bx1 = int(round(bbox.get("x1", 0)))
                by1 = int(round(bbox.get("y1", 0)))
                bx2 = int(round(bbox.get("x2", 0)))
                by2 = int(round(bbox.get("y2", 0)))
                class_name = det.get("class_name", "Dị vật")
                conf = det.get("confidence", 0.0)
                label = f"{class_name} {conf:.2f}"
                # Viền màu đỏ nổi bật (0, 0, 255), độ dày 2px
                cv2.rectangle(annotated_image, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
                # Vẽ nền chữ nhật màu đỏ chữ trắng
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                bg_y1 = max(0, by1 - th - 8)
                cv2.rectangle(annotated_image, (bx1, bg_y1), (bx1 + tw + 6, by1), (0, 0, 255), -1)
                cv2.putText(
                    annotated_image,
                    label,
                    (bx1 + 3, by1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

        return {
            "score": score,
            "heatmap": heatmap,
            "detections": detections,
            "objects": detections,
            "anomaly_boxes": anomaly_boxes,
            "roi": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "threshold_applied": float(threshold),
            "image": annotated_image,
        }

    def compare(
        self,
        standard_data: Any,
        runtime_data: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """So sánh điểm số bất thường runtime và dị vật phát hiện với cấu hình chuẩn.

        Quy tắc phán định:
        1. Nếu runtime_score <= threshold: Kết luận OK (vùng bình thường, không có bất thường).
        2. Nếu runtime_score > threshold:
           - Nếu có phát hiện dị vật YOLO (len(detections) > 0): Kết luận NG.
           - Nếu không phát hiện dị vật YOLO (len(detections) == 0): Kết luận OK.

        Args:
            standard_data (Any): Dữ liệu cấu hình chuẩn (có thể là float/int ngưỡng,
                hoặc dict chứa key "threshold", hoặc bool).
            runtime_data (Dict[str, Any]): Dữ liệu đầu ra từ phương thức ``define``.

        Returns:
            Dict[str, Any]: Dữ liệu so sánh tổng hợp gồm:
                - "standard_threshold" (float): Ngưỡng điểm bất thường cài đặt.
                - "runtime_score" (float): Điểm bất thường thực tế.
                - "detections" (List[Dict[str, Any]]): Danh sách đối tượng dị vật phát hiện.
                - "detections_count" (int): Số lượng dị vật phát hiện.
                - "ok" (bool): Trạng thái phán định tổng hợp.
                - "message" (str): Thông điệp mô tả chi tiết kết quả.
                - "image" (np.ndarray): Ảnh kết quả trực quan.
                - "heatmap" (np.ndarray | None): Bản đồ nhiệt bất thường.

        Raises:
            ValueError: Nếu runtime_data không phải là dict hoặc thiếu trường "score".
        """
        if not isinstance(runtime_data, dict) or "score" not in runtime_data:
            raise ValueError("runtime_data phải là dict chứa ít nhất trường 'score'")

        # Phân tích ngưỡng từ standard_data
        threshold = 0.2  # Ngưỡng mặc định
        if isinstance(standard_data, (int, float)):
            threshold = float(standard_data)
        elif isinstance(standard_data, dict):
            if "threshold" in standard_data:
                threshold = float(standard_data["threshold"])
            elif "ForeignObjectInspector" in standard_data and isinstance(
                standard_data["ForeignObjectInspector"], dict
            ):
                threshold = float(
                    standard_data["ForeignObjectInspector"].get("threshold", 0.2)
                )

        runtime_score = float(runtime_data.get("score", 0.0))
        detections: List[Dict[str, Any]] = runtime_data.get("detections", [])
        detections_count = len(detections)

        # Áp dụng logic phán định
        if runtime_score <= threshold:
            ok = True
            message = (
                f"Điểm bất thường ({runtime_score:.4f}) <= ngưỡng ({threshold:.4f}): ĐẠT chuẩn"
            )
        else:
            if detections_count > 0:
                ok = False
                detected_names = []
                for d in detections:
                    c_name = d.get("class_name", "Không rõ")
                    vn_name = FOREIGN_CLASS_NAME_VIETNAMESE_MAP.get(c_name, c_name)
                    detected_names.append(vn_name)
                names_str = ", ".join(detected_names)
                
                message = (
                    f"Điểm bất thường ({runtime_score:.4f}) > ngưỡng ({threshold:.4f}) "
                    f"và phát hiện {detections_count} dị vật bất thường ({names_str})"
                )
            else:
                ok = True
                message = (
                    f"Điểm bất thường ({runtime_score:.4f}) > ngưỡng ({threshold:.4f}) "
                    f"nhưng không phát hiện dị vật YOLO: ĐẠT chuẩn"
                )

        return {
            "standard_threshold": threshold,
            "runtime_score": runtime_score,
            "detections": detections,
            "detections_count": detections_count,
            "anomaly_boxes": runtime_data.get("anomaly_boxes", []),
            "ok": ok,
            "message": message,
            "image": runtime_data.get("image"),
            "heatmap": runtime_data.get("heatmap"),
            "roi": runtime_data.get("roi"),
        }

    def judge(self, comparison_data: Dict[str, Any]) -> JudgmentResult:
        """Thực hiện kết luận phán định cuối cùng trả về đối tượng JudgmentResult.

        Args:
            comparison_data (Dict[str, Any]): Dữ liệu đầu ra từ phương thức ``compare``.

        Returns:
            JudgmentResult: Kết quả chuẩn hóa chứa trạng thái OK/NG, dữ liệu chuẩn,
                dữ liệu runtime, thông điệp và danh sách lỗi.

        Raises:
            ValueError: Nếu comparison_data thiếu các khóa bắt buộc.
        """
        required_keys = {"ok", "standard_threshold", "runtime_score", "message"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu các trường bắt buộc")

        ok: bool = bool(comparison_data["ok"])
        message: str = str(comparison_data["message"])
        errors: List[str] = [] if ok else [message]

        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"threshold": comparison_data["standard_threshold"]},
            runtime_data={
                "score": comparison_data["runtime_score"],
                "detections": comparison_data.get("detections", []),
                "detections_count": comparison_data.get("detections_count", 0),
                "anomaly_boxes": comparison_data.get("anomaly_boxes", []),
                "image": comparison_data.get("image"),
                "heatmap": comparison_data.get("heatmap"),
                "roi": comparison_data.get("roi"),
            },
            comparison_data=comparison_data,
            message=message,
            errors=errors,
        )
