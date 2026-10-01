import threading
import cv2
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union

from app.engines.AI_model_process.frame_patch_core_process import FrameModelPatchCore
from app.utils.opencv_tool import Tool_OpenCv2
from .base_ai import BaseJudgerAI, JudgmentResult


class EndChippingDetector(BaseJudgerAI):
    """Bộ phán định mẻ đầu ống (End Chipping Detector) sử dụng PatchCore.

    Sử dụng mô hình PatchCore để kiểm tra bất thường và phát hiện các vị trí
    bị mẻ ở phần đầu ống trong vùng ROI được cấu hình.
    """

    INSPECTOR_NAME = "EndChippingInspector"

    def __init__(
        self,
        end_chipping_model: Optional[FrameModelPatchCore] = None,
        end_chipping_service: Optional[Any] = None,
    ) -> None:
        """Khởi tạo detector phát hiện mẻ đầu ống.

        Args:
            end_chipping_model (FrameModelPatchCore, optional): Instance mô hình PatchCore cố định.
            end_chipping_service (Any, optional): Service nạp động mô hình PatchCore theo
                từng point (product_id, frame_id, item_id).

        Raises:
            TypeError: Nếu cả hai tham số đều None hoặc model truyền vào không hợp lệ.
        """
        super().__init__()
        if end_chipping_model is None and end_chipping_service is None:
            raise TypeError("end_chipping_model hoặc end_chipping_service phải được cung cấp")
        if end_chipping_model is not None and not hasattr(
            end_chipping_model, "predict_with_anomaly_boxes"
        ):
            raise TypeError(
                "end_chipping_model phải có phương thức predict_with_anomaly_boxes"
            )
        self.end_chipping_model = end_chipping_model
        self.end_chipping_service = end_chipping_service

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
        """Trích xuất dữ liệu bất thường và phát hiện mẻ đầu ống runtime từ ảnh gốc và ROI.

        Gọi ``predict_with_anomaly_boxes`` để tính điểm số bất thường (score),
        bản đồ nhiệt (heatmap), và các bounding box vùng mẻ theo ngưỡng threshold.
        Ảnh runtime đầu ra chỉ vẽ các vùng lỗi; không phủ heatmap lên ROI để tránh
        che các lớp vẽ khác (polygon, line, ...).

        Args:
            img (np.ndarray): Mảng ảnh gốc đầu vào (định dạng BGR/RGB).
            x1 (int): Tọa độ X góc trái trên của vùng kiểm tra (ROI).
            y1 (int): Tọa độ Y góc trái trên của vùng kiểm tra (ROI).
            x2 (int): Tọa độ X góc phải dưới của vùng kiểm tra (ROI).
            y2 (int): Tọa độ Y góc phải dưới của vùng kiểm tra (ROI).
            threshold (float, optional): Ngưỡng điểm bất thường dùng để trích xuất
                vùng mẻ. Mặc định là 0.0.
            **kwargs: Các tham số bổ sung như product_id, frame_id, item_id.

        Returns:
            Dict[str, Any]: Dictionary chứa:
                - "score" (float): Điểm bất thường của toàn vùng ảnh ROI.
                - "heatmap" (np.ndarray | None): Bản đồ nhiệt trực quan vùng bất thường.
                - "anomaly_boxes" (List[Tuple[int, int, int, int]]): Danh sách bounding box vùng lỗi.
                - "roi" (Dict[str, int]): Tọa độ ROI x1, y1, x2, y2 đã kiểm tra.
                - "threshold_applied" (float): Ngưỡng đã dùng khi define.
                - "image" (np.ndarray): Ảnh đã vẽ vùng lỗi bằng tiếng Việt, không phủ heatmap ROI.

        Raises:
            ValueError: Nếu ảnh rỗng, tọa độ ROI không hợp lệ hoặc thiếu thông tin point.
            RuntimeError: Nếu chưa có model khả dụng.
        """
        if not isinstance(img, np.ndarray) or img.size == 0:
            raise ValueError("img đầu vào không được rỗng")
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Tọa độ ROI không hợp lệ: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        model = self.end_chipping_model
        if model is None and self.end_chipping_service is not None:
            product_id = kwargs.get("product_id")
            frame_id = kwargs.get("frame_id")
            item_id = kwargs.get("item_id")
            if product_id is None or frame_id is None or item_id is None:
                raise ValueError(
                    f"Thiếu thông tin product_id, frame_id, item_id để nạp mô hình: {kwargs}"
                )
            model = self.end_chipping_service.get_patchcore_frame(product_id, frame_id, item_id)
        if model is None:
            raise RuntimeError("Chưa có end_chipping_model để thực thi")

        score, heatmap, anomaly_boxes = model.predict_with_anomaly_boxes(
            img, x1, y1, x2, y2, threshold=float(threshold)
        )

        score = float(score)

        save_runtime_images = kwargs.get("saveRuntimeImages", False)
        if str(save_runtime_images).lower() == "true":
            p_id = kwargs.get("product_id")
            f_id = kwargs.get("frame_id")
            i_id = kwargs.get("item_id")
            if p_id is not None and f_id is not None and i_id is not None and self.end_chipping_service is not None:
                roi_img = img[y1:y2, x1:x2].copy()
                threading.Thread(
                    target=self.end_chipping_service.save_runtime_image_for_training,
                    args=(p_id, f_id, i_id, roi_img),
                    daemon=True,
                ).start()

        # Tạo bản sao ảnh để vẽ kết quả trực quan phục vụ UI và xuất kết quả
        annotated_image = img.copy()

        # Chỉ vẽ khung và nhãn vùng lỗi, không phủ heatmap để tránh che lớp vẽ khác.
        for idx, abox in enumerate(anomaly_boxes):
            px, py, pw, ph = (int(v) for v in abox)
            Tool_OpenCv2.draw_labeled_roi(
                annotated_image,
                (px, py, px + pw, py + ph),
                f"Vùng lỗi {idx + 1}",
                (0, 215, 255),
                thickness=2,
            )

        return {
            "score": score,
            "heatmap": heatmap,
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
        """So sánh điểm số bất thường mẻ đầu ống runtime với cấu hình chuẩn.

        Quy tắc phán định:
        1. Nếu runtime_score <= threshold: Kết luận OK (vùng đầu ống bình thường, không mẻ).
        2. Nếu runtime_score > threshold: Kết luận NG (phát hiện mẻ đầu ống).

        Args:
            standard_data (Any): Dữ liệu cấu hình chuẩn (có thể là float/int ngưỡng,
                hoặc dict chứa key "threshold", hoặc dict theo tên inspector).
            runtime_data (Dict[str, Any]): Dữ liệu đầu ra từ phương thức ``define``.

        Returns:
            Dict[str, Any]: Dữ liệu so sánh tổng hợp gồm:
                - "standard_threshold" (float): Ngưỡng điểm bất thường cài đặt.
                - "runtime_score" (float): Điểm bất thường thực tế.
                - "anomaly_boxes" (List[Tuple[int, int, int, int]]): Danh sách box vùng lỗi.
                - "ok" (bool): Trạng thái phán định.
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
            elif "EndChippingInspector" in standard_data and isinstance(
                standard_data["EndChippingInspector"], dict
            ):
                threshold = float(
                    standard_data["EndChippingInspector"].get("threshold", 0.2)
                )

        runtime_score = float(runtime_data.get("score", 0.0))
        anomaly_boxes = runtime_data.get("anomaly_boxes", [])

        # Áp dụng logic phán định
        if runtime_score <= threshold:
            ok = True
            message = "Không phát hiện sự bất thường"
        else:
            ok = False
            message = "Phát hiện sự bất thường"

        return {
            "standard_threshold": threshold,
            "runtime_score": runtime_score,
            "anomaly_boxes": anomaly_boxes,
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
            ValueError: Nếu comparison_data thiếu các trường bắt buộc.
        """
        required_keys = {"ok", "standard_threshold", "runtime_score", "message"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu các trường bắt buộc")

        ok: bool = bool(comparison_data["ok"])
        message: str = "Không phát hiện sự bất thường" if ok else "Phát hiện sự bất thường"
        errors: List[str] = []
        if not ok:
            errors.append(
                f"[Mẻ đầu ống] NG - \"Mẻ đầu ống\" - Quy định:\"Không phát hiện sự bất thường\" - Thực tế :\"Phát hiện sự bất thường\""
            )

        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"threshold": comparison_data["standard_threshold"]},
            runtime_data={
                "score": comparison_data["runtime_score"],
                "anomaly_boxes": comparison_data.get("anomaly_boxes", []),
                "image": comparison_data.get("image"),
                "heatmap": comparison_data.get("heatmap"),
                "roi": comparison_data.get("roi"),
            },
            comparison_data=comparison_data,
            message=message,
            errors=errors,
        )
