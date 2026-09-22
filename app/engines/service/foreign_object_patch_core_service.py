"""PatchCore service cho workflow kiểm tra dị vật."""

import base64
from pathlib import Path

import cv2
import faiss
import torch

from app.config import PATH_FOLDER_MODEL_DETECT_PATCH_CORE
from app.config import PATH_FILE_FOREIGN_PATCHCORE_TRAIN_MANIFEST
from app.config import PatchCoreAnomalyConfig
from app.core import ErrorCode, Result
from app.engines.AI_model_process import FrameModelPatchCore, FramePatchCoreObjectDetector
from app.engines.model_AI import ModelPatchCore
from app.engines.service.patchcore_inspection_service import PatchCoreInspectionService
from app.engines.train.patchcore_train_model.patchcore_train_record_repository import (
    PatchCoreTrainRecordRepository,
)


class ForeignObjectPatchCoreService(PatchCoreInspectionService):
    """Tạo model PatchCore Dị vật với manifest riêng và session foreign."""

    def __init__(self, point_service, yolo_object_model=None):
        """Khởi tạo service kiểm tra dị vật.

        Args:
            point_service: Service truy xuất ảnh product/frame/item.
            yolo_object_model: Model YOLO object dùng để nhận diện trong vùng
                bất thường PatchCore.

        Returns:
            None.

        Raises:
            OSError: Nếu không thể tạo thư mục chứa manifest.
        """
        super().__init__(
            point_service=point_service,
            roi_name="foreign",
            purpose="train patchcore foreign object",
            record_repository=PatchCoreTrainRecordRepository(
                manifest_path=PATH_FILE_FOREIGN_PATCHCORE_TRAIN_MANIFEST,
            ),
        )
        self.yolo_object_model = yolo_object_model

    def run_model_with_object_detection(
        self,
        product_id: int,
        frame_id: int,
        item_id: int,
        crop_roi: dict,
        width_canvas: int | None = None,
    ) -> dict:
        """Chạy PatchCore và nhận diện YOLO trên từng vùng bất thường.

        Args:
            product_id: Mã sản phẩm.
            frame_id: Mã frame.
            item_id: Mã item/point.
            crop_roi: ROI cần kiểm tra theo ảnh hoặc canvas.
            width_canvas: Chiều rộng canvas nếu ROI dùng tọa độ canvas.

        Returns:
            dict: Kết quả PatchCore gồm ảnh overlay, score, box bất thường,
                ảnh crop từng vùng bất thường và detection YOLO.

        Raises:
            ValueError: Nếu model đang bận, ROI không hợp lệ hoặc chưa có YOLO.
            OSError: Nếu không đọc được ảnh hoặc model PatchCore.
        """
        if self.yolo_object_model is None:
            raise ValueError("Chưa cấu hình model YOLO object cho foreign object")
        if self.worker._thread is not None and self.worker._thread.is_alive():
            raise ValueError("Đang bận tạo model, vui lòng chờ hoàn tất")
        if not self._inference_lock.acquire(blocking=False):
            raise ValueError("Đang bận chạy inference")

        model = None
        try:
            image_result = self.point_service.get_path_img_point(product_id, frame_id, item_id)
            if not image_result.ok:
                return Result.Fail(image_result.error).to_dict()
            image_bgr = cv2.imread(str(image_result.data))
            if image_bgr is None:
                return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()

            converted_roi = self._convert_crop_roi(crop_roi, image_bgr.shape, width_canvas)
            cropped_bgr = image_bgr[
                converted_roi["yStart"]:converted_roi["yEnd"],
                converted_roi["xStart"]:converted_roi["xEnd"],
            ]
            model_root = (
                Path(PATH_FOLDER_MODEL_DETECT_PATCH_CORE)
                / str(product_id)
                / str(frame_id)
                / str(item_id)
            )
            model_file = self._find_latest_model(model_root)
            if model_file is None:
                return Result.Fail(ErrorCode.PATCHCORE_MODEL_NOT_FOUND).to_dict()

            image_rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)
            index_probe = faiss.read_index(str(model_file))
            config = PatchCoreAnomalyConfig(
                index_path=str(model_file),
                nprobe=max(1, int(index_probe.nlist)),
                img_size=256,
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
            model = ModelPatchCore(config)
            model.load_model()
            score, overlay_bgr = model.predict(image_rgb)
            boxes = [
                (int(x), int(y), int(width), int(height))
                for x, y, width, height in model.get_bounding_boxes(image_rgb)
            ]

            detector = FramePatchCoreObjectDetector(
                FrameModelPatchCore(model),
                self.yolo_object_model,
            )
            detections = detector.detect_anomaly_objects(
                cropped_bgr,
                0,
                0,
                cropped_bgr.shape[1],
                cropped_bgr.shape[0],
                anomaly_boxes=boxes,
            )
            anomaly_regions = self._encode_anomaly_regions(cropped_bgr, boxes)

            ok, encoded = cv2.imencode(".png", overlay_bgr)
            if not ok:
                raise ValueError("Không thể mã hóa ảnh inference")
            return Result.Ok({
                "image": "data:image/png;base64," + base64.b64encode(encoded).decode("ascii"),
                "score": float(score),
                "boxes": [self._box_to_dict(box) for box in boxes],
                "anomaly_regions": anomaly_regions,
                "detections": detections,
                "status": "NG" if boxes else "OK",
                "model_file": str(model_file),
            }).to_dict()
        finally:
            if model is not None:
                model.unload()
            self._inference_lock.release()

    @staticmethod
    def _box_to_dict(box: tuple[int, int, int, int]) -> dict[str, int]:
        """Chuyển box ``(x, y, width, height)`` thành object response."""
        x, y, width, height = box
        return {"x": x, "y": y, "width": width, "height": height}

    @staticmethod
    def _encode_anomaly_regions(
        image_bgr,
        boxes: list[tuple[int, int, int, int]],
    ) -> list[dict]:
        """Crop và mã hóa PNG từng vùng PatchCore bất thường."""
        regions = []
        image_height, image_width = image_bgr.shape[:2]
        for index, (x, y, width, height) in enumerate(boxes, start=1):
            left = max(0, x)
            top = max(0, y)
            right = min(image_width, x + width)
            bottom = min(image_height, y + height)
            crop = image_bgr[top:bottom, left:right]
            if crop.size == 0:
                continue
            ok, encoded = cv2.imencode(".png", crop)
            if not ok:
                continue
            regions.append({
                "index": index,
                "box": {
                    "x": left,
                    "y": top,
                    "width": right - left,
                    "height": bottom - top,
                },
                "image": "data:image/png;base64," + base64.b64encode(encoded).decode("ascii"),
            })
        return regions