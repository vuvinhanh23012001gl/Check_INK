from app.container import ServiceContainer,EnumMode
from app.core.context import RuntimePipelineState
from pathlib import Path
from datetime import datetime, timezone
import cv2
import time

class StageTransform:
    def __init__(self,services:ServiceContainer):
        self.services =  services

    def run(self):
        """Di chuyển, chụp ảnh và phán định toàn bộ point của sản phẩm.

        Input: ``services.prepared_product`` từ Stage 1.
        Output: danh sách kết quả point lưu vào runtime state và chuyển Stage 3.
        Errors: ``RuntimeError`` khi phần cứng, di chuyển hoặc camera thất bại.
        """
        prepared = self.services.prepared_product
        if prepared is None:
            raise RuntimeError("Stage 2 chưa nhận dữ liệu từ Stage 1")
        self.services.runtime_state.set_pipeline_state(RuntimePipelineState.RUNNING)
        self.services.runtime_state.set_judgment_running(True)
        results = []
        try:
            for frame in prepared.frames:
                for point in frame["points"]:
                    self._ensure_running()
                    result = self._process_point(prepared, frame, point)
                    results.append(result)
                    self.services.queue_data_send_client.put({
                        "type": "data_output_judment",
                        "data": result,
                    })
            if not self.services.obj_iai_control.move_to_point(0, 0, 0):
                raise RuntimeError("IAI không về được vị trí 0,0,0 sau sản phẩm")
            self.services.runtime_state.set_product_result(results)
            self.services.set_mode(EnumMode.MODE_EXPORT)
            return results
        finally:
            self.services.runtime_state.set_judgment_running(False)

    def _ensure_running(self) -> None:
        """Dừng stage nếu người dùng yêu cầu stop hoặc IAI đang ở lỗi."""
        if self.services.runtime_state.is_stop_requested():
            raise RuntimeError("Pipeline đã nhận yêu cầu dừng")
        if self.services.obj_iai_control.get_status().name == "STOP":
            raise RuntimeError("IAI đang ở trạng thái STOP")

    def _process_point(self, prepared, frame: dict, point: dict) -> dict:
        """Xử lý một point và trả về payload JSON hóa được."""
        frame_id = frame["frame_id"]
        point_id = point["point_id"]
        self.services.send_judgment_log(f"▶ Đang chạy frame {frame_id}, point {point_id}")
        if not self._move_with_retry(point):
            raise RuntimeError(f"IAI di chuyển thất bại tại frame {frame_id}, point {point_id}")
        image = self._capture_with_retry()
        image_path = self._save_image(image, prepared.product_id, frame_id, point_id)
        summary = self.services.obj_judment.run_summary(
            image=image,
            inspectors=point["judgment"],
            scale_mm_per_pixel=prepared.scale_mm_per_pixel,
        )
        summary.update({
            "product_id": prepared.product_id,
            "frame_id": frame_id,
            "point_id": point_id,
            "iai": {key: point[key] for key in ("x", "y", "z")},
            "image_path": image_path,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        })
        self.services.send_judgment_log(
            f"{'✅' if summary['overall'] else '❌'} Frame {frame_id}, point {point_id}: "
            f"{summary['status']}"
        )
        return summary

    def _move_with_retry(self, point: dict) -> bool:
        """Gửi lệnh di chuyển với số lần thử cấu hình trong IAIConfig."""
        attempts = max(1, int(getattr(self.services.obj_iai_config, "move_retry_count", 3)))
        timeout = float(getattr(self.services.obj_iai_config, "move_timeout", 4))
        for attempt in range(1, attempts + 1):
            if self.services.obj_iai_control.move_to_point(
                point["x"], point["y"], point["z"], timeout=timeout
            ):
                return True
            self.services.send_judgment_log(
                f"⚠️ Di chuyển frame {point.get('frame_id', '')}/point "
                f"{point['point_id']} thất bại lần {attempt}/{attempts}"
            )
        return False

    def _capture_with_retry(self):
        """Chụp ảnh camera với số lần thử cấu hình."""
        attempts = max(1, int(getattr(self.services.obj_iai_config, "capture_retry_count", 3)))
        timeout = float(getattr(self.services.obj_iai_config, "capture_timeout", 1))
        for attempt in range(1, attempts + 1):
            status, image = self.services.obj_camera.capture_once(timeout=timeout)
            if status and image is not None:
                return image
            self.services.send_judgment_log(f"⚠️ Camera lỗi lần {attempt}/{attempts}")
        raise RuntimeError("Camera không chụp được ảnh")

    def _save_image(self, image, product_id: str, frame_id: str, point_id: str) -> str:
        """Lưu ảnh point vào app/output và trả về đường dẫn tương đối."""
        output_dir = Path(__file__).resolve().parents[1] / "output" / "judgment" / product_id / frame_id
        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = output_dir / f"point_{point_id}.jpg"
        if not cv2.imwrite(str(image_path), image):
            raise RuntimeError(f"Không lưu được ảnh phán định: {image_path}")
        return str(image_path.relative_to(Path(__file__).resolve().parents[1]))