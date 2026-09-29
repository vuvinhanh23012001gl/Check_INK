import base64
from pathlib import Path
import cv2
import faiss
# pyrefly: ignore [missing-import]
import torch
from app.config import (
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
    PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST,
    PatchCoreAnomalyConfig,
)
from app.core import ErrorCode, Result
from app.engines.AI_model_process.frame_patch_core_process import FrameModelPatchCore
from app.engines.model_AI import ModelPatchCore
from app.engines.service.patchcore_inspection_service import PatchCoreInspectionService
from app.engines.train.patchcore_train_model.patchcore_train_record_repository import (
    PatchCoreTrainRecordRepository,
)


class EndChippingPatchCoreService(PatchCoreInspectionService):
    """Cấu hình PatchCore cho kiểm tra đầu ống mẻ."""
    training_inspector_name = "EndChippingInspector"

    def __init__(self, point_service):
        """Khởi tạo service End Chipping với manifest riêng.

        Args:
            point_service: Service truy xuất ảnh theo product/frame/item.

        Returns:
            None.

        Raises:
            OSError: Nếu không thể tạo thư mục chứa manifest.
        """
        super().__init__(
            point_service=point_service,
            roi_name="end_chipping",
            purpose="train patchcore end chipping",
            record_repository=PatchCoreTrainRecordRepository(
                manifest_path=PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST,
            ),
        )

    def get_patchcore_frame(
        self,
        product_id: int | str,
        frame_id: int | str,
        item_id: int | str,
    ) -> FrameModelPatchCore:
        """Lấy hoặc nạp cached FrameModelPatchCore cho một point.

        Args:
            product_id: Mã sản phẩm.
            frame_id: Mã frame.
            item_id: Mã item/point.

        Returns:
            FrameModelPatchCore: Instance xử lý mô hình PatchCore.

        Raises:
            FileNotFoundError: Nếu không tìm thấy file index mô hình.
        """
        key = (str(product_id), str(frame_id), str(item_id))
        model_root = (
            Path(PATH_FOLDER_MODEL_DETECT_PATCH_CORE)
            / str(product_id)
            / str(frame_id)
            / str(item_id)
        )
        model_file = self._find_latest_model(model_root)
        if model_file is None:
            raise FileNotFoundError(
                f"Không tìm thấy mô hình PatchCore tại {model_root} "
                f"cho sản phẩm {product_id}, frame {frame_id}, item {item_id}"
            )

        if not hasattr(self, "_patchcore_cache"):
            self._patchcore_cache: dict[tuple[str, str, str], tuple[Path, FrameModelPatchCore]] = {}

        if key in self._patchcore_cache:
            cached_path, cached_frame = self._patchcore_cache[key]
            if cached_path == model_file:
                return cached_frame

        index_probe = faiss.read_index(str(model_file))
        try:
            nlist = int(faiss.extract_index_ivf(index_probe).nlist)
        except Exception:
            nlist = getattr(index_probe, "nlist", 1)
        config = PatchCoreAnomalyConfig(
            index_path=str(model_file),
            nprobe=max(1, nlist),
            img_size=256,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
        model = ModelPatchCore(config)
        model.load_model()
        model.warmup()
        patchcore_frame = FrameModelPatchCore(model)
        self._patchcore_cache[key] = (model_file, patchcore_frame)
        return patchcore_frame

    def run_model(
        self,
        product_id: int,
        frame_id: int,
        item_id: int,
        crop_roi: dict,
        width_canvas: int | None = None,
    ) -> dict:
        """Chạy inference model PatchCore mẻ đầu ống của một Point và vẽ viền vàng cam như runtime.

        Args:
            product_id: Mã sản phẩm.
            frame_id: Mã frame.
            item_id: Mã item/point.
            crop_roi: Tọa độ vùng crop trên canvas hoặc ảnh.
            width_canvas: Chiều rộng canvas nếu crop_roi ở hệ canvas.

        Returns:
            dict: Kết quả inference kèm ảnh overlay có heatmap và bounding boxes viền vàng cam.

        Raises:
            ValueError: Nếu worker bận hoặc ROI không hợp lệ.
        """
        if self.worker._thread is not None and self.worker._thread.is_alive():
            raise ValueError("Đang bận tạo model, vui lòng chờ hoàn tất")
        if not self._inference_lock.acquire(blocking=False):
            raise ValueError("Đang bận chạy inference")
        try:
            image_result = self.point_service.get_path_img_point(product_id, frame_id, item_id)
            if not image_result.ok:
                return Result.Fail(image_result.error).to_dict()
            image_bgr = cv2.imread(str(image_result.data))
            if image_bgr is None:
                return Result.Fail(ErrorCode.IMAGE_NOT_FOUND).to_dict()

            converted_roi = self._convert_crop_roi(crop_roi, image_bgr.shape, width_canvas)
            x1 = int(converted_roi["xStart"])
            y1 = int(converted_roi["yStart"])
            x2 = int(converted_roi["xEnd"])
            y2 = int(converted_roi["yEnd"])

            cropped_bgr = image_bgr[y1:y2, x1:x2]
            self._save_retrain_input(cropped_bgr)

            patchcore_frame = self.get_patchcore_frame(product_id, frame_id, item_id)
            threshold_val = (
                float(crop_roi.get("threshold", 0.1))
                if isinstance(crop_roi, dict) and "threshold" in crop_roi
                else 0.1
            )

            score, overlay_bgr, anomaly_boxes = patchcore_frame.predict_with_anomaly_boxes(
                image_bgr, x1, y1, x2, y2, threshold=threshold_val
            )

            # Vẽ viền vàng cam (0, 215, 255) và nhãn Vung loi #... lên overlay_bgr giống runtime ForeignObjectInspector
            for idx, abox in enumerate(anomaly_boxes):
                bx = abox[0] - x1
                by = abox[1] - y1
                bw = abox[2]
                bh = abox[3]
                cv2.rectangle(overlay_bgr, (bx, by), (bx + bw, by + bh), (0, 215, 255), 2)
                label_anom = f"Vung loi #{idx + 1}"
                (tw, th), _ = cv2.getTextSize(label_anom, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                bg_y1 = max(0, by - th - 6)
                cv2.rectangle(overlay_bgr, (bx, bg_y1), (bx + tw + 6, by), (0, 215, 255), -1)
                cv2.putText(
                    overlay_bgr,
                    label_anom,
                    (bx + 3, by - 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                    cv2.LINE_AA,
                )

            ok, encoded = cv2.imencode(".png", overlay_bgr)
            if not ok:
                raise ValueError("Không thể mã hóa ảnh inference")

            boxes_crop = [
                {"x": int(b[0] - x1), "y": int(b[1] - y1), "width": int(b[2]), "height": int(b[3])}
                for b in anomaly_boxes
            ]
            return Result.Ok({
                "image": "data:image/png;base64," + base64.b64encode(bytes(encoded)).decode("ascii"),
                "score": float(score),
                "boxes": boxes_crop,
                "status": "NG" if boxes_crop else "OK",
            }).to_dict()
        finally:
            self._inference_lock.release()

