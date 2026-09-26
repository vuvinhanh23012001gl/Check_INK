from app.container import ServiceContainer,EnumMode
from app.core.context import RuntimePipelineState
from pathlib import Path
from datetime import datetime, timezone
import cv2
import json
import shutil
import time

class StageTransform:
    INSPECTOR_DISPLAY_NAMES = {
        "AirBubblesItemInspector": "Bọt khí đường hàn",
        "MeasurementWeldInspector": "Độ rộng đường hàn",
        "SlitWeldInspector": "Đường xẻ mối hàn",
        "ArmSensorInspector": "ARM Sensor",
        "ArmCoverInspector": "ARM Cover",
        "BorderFilmInspector": "Biên film",
        "MembraneInspector": "Màng bán thấm",
        "HoleItemInspector": "Lỗ thủng",
        "ScratchedPipeItemInspector": "Vết trầy xước",
        "EndChippingInspector": "Mẻ cạnh",
        "ForeignObjectInspector": "Dị vật",
    }

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
        print(
            f"[STAGE2] Bắt đầu session={prepared.session_id}, "
            f"product={prepared.product_id}, number_step={prepared.number_step}"
        )
        self.services.runtime_state.set_pipeline_state(RuntimePipelineState.RUNNING)
        self.services.runtime_state.set_judgment_running(True)
        results = []
        step = 0
        self._send_client({
            "type": "judgment_reset",
            "data": {
                "product_id": prepared.product_id,
                "number_step": prepared.number_step,
                "session_id": prepared.session_id,
            },
        })
        try:
            for frame in prepared.frames:
                for point in frame["points"]:
                    self._ensure_running()
                    step += 1
                    try:
                        result = self._process_point(prepared, frame, point, step)
                    except Exception as error:
                        result = {
                            "product_id": prepared.product_id,
                            "frame_id": frame["frame_id"],
                            "item_id": point["point_id"],
                            "session_id": prepared.session_id,
                            "status": "ERROR",
                            "overall": False,
                            "number_step": prepared.number_step,
                            "step": step,
                            "inspectors": {},
                            "message": str(error),
                        }
                        self._send_client({"type": "judgment_item_result", "data": result})
                        raise
                    results.append(result)
                    self._send_client({"type": "judgment_item_result", "data": result})
            if not self.services.obj_iai_control.move_to_point(0, 0, 0):
                raise RuntimeError("IAI không về được vị trí 0,0,0 sau sản phẩm")
            self.services.runtime_state.set_product_result(results)
            self._send_client({
                "type": "judgment_product_result",
                "data": {
                    "product_id": prepared.product_id,
                    "session_id": prepared.session_id,
                    "number_step": prepared.number_step,
                    "overall": all(result.get("overall") is True for result in results),
                    "status": "OK" if all(result.get("overall") is True for result in results) else "NG",
                    "items": results,
                },
            })
            self.services.set_mode(EnumMode.MODE_EXPORT)
            return results
        except Exception as error:
            self._send_client({
                "type": "judgment_product_result",
                "data": {
                    "product_id": prepared.product_id,
                    "session_id": prepared.session_id,
                    "number_step": prepared.number_step,
                    "overall": False,
                    "status": "NG",
                    "error": str(error),
                    "items": results,
                },
            })
            raise
        finally:
            self.services.runtime_state.set_judgment_running(False)

    def _ensure_running(self) -> None:
        """Dừng stage nếu người dùng yêu cầu stop hoặc IAI đang ở lỗi."""
        if self.services.runtime_state.is_stop_requested():
            raise RuntimeError("Pipeline đã nhận yêu cầu dừng")
        if self.services.obj_iai_control.get_status().name == "STOP":
            raise RuntimeError("IAI đang ở trạng thái STOP")

    def _process_point(self, prepared, frame: dict, point: dict, step: int) -> dict:
        """Xử lý một point và trả về payload JSON hóa được."""
        frame_id = frame["frame_id"]
        point_id = point["point_id"]
        inspectors = point.get("judgment") or {}
        print(
            f"[STAGE2] step={step}/{prepared.number_step}, "
            f"frame={frame_id}, item={point_id}, inspectors={list(inspectors.keys())}"
        )
        if not inspectors:
            self.services.send_judgment_log(
                f"⚠️ Frame {frame_id}, point {point_id}: không có dữ liệu master phán định."
            )
            judgment_path = self._save_master_result(prepared, frame, point, step)
            return {
                "product_id": prepared.product_id,
                "frame_id": frame_id,
                "item_id": point_id,
                "session_id": prepared.session_id,
                "status": "NO_DATA",
                "overall": False,
                "number_step": prepared.number_step,
                "step": step,
                "judgment_path": judgment_path,
                "inspectors": {},
                "message": "Không có dữ liệu master phán định.",
            }
        self.services.send_judgment_log(f"▶ Đang chạy frame {frame_id}, point {point_id}")
        print(f"[STAGE2] Di chuyển IAI đến frame={frame_id}, item={point_id}: {point['x']},{point['y']},{point['z']}")
        if not self._move_with_retry(point):
            raise RuntimeError(f"IAI di chuyển thất bại tại frame {frame_id}, point {point_id}")
        image = self._capture_with_retry()
        print(f"[STAGE2] Đã chụp ảnh frame={frame_id}, item={point_id}; bắt đầu Judment.run_summary.")
        image_path = self._save_image(image, prepared, frame_id, point_id)
        summary = self.services.obj_judment.run_summary(
            image=image,
            inspectors=inspectors,
            scale_mm_per_pixel=prepared.scale_mm_per_pixel,
        )
        print(
            f"[STAGE2] Kết thúc phán định frame={frame_id}, item={point_id}: "
            f"status={summary.get('status')}, overall={summary.get('overall')}"
        )
        for inspector_name, inspector_result in summary.get("inspectors", {}).items():
            inspector_result["display_name"] = self.INSPECTOR_DISPLAY_NAMES.get(
                inspector_name,
                inspector_name,
            )
        judgment_path = self._output_url(
            self._session_item_dir(prepared, frame_id, point_id) / "judgment.jpg"
        )
        summary.update({
            "product_id": prepared.product_id,
            "frame_id": frame_id,
            "point_id": point_id,
            "item_id": point_id,
            "session_id": prepared.session_id,
            "number_step": prepared.number_step,
            "step": step,
            "iai": {key: point[key] for key in ("x", "y", "z")},
            "judgment_path": judgment_path,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        })
        judgment_path = self._save_judgment_result(
            image,
            prepared,
            frame_id,
            point_id,
            summary,
        )
        summary["judgment_path"] = judgment_path
        self.services.send_judgment_log(
            f"{'✅' if summary['overall'] else '❌'} Frame {frame_id}, point {point_id}: "
            f"{summary['status']}"
        )
        return summary

    def _send_client(self, payload: dict) -> None:
        """Đưa sự kiện phán định vào queue gửi Socket.IO."""
        self.services.queue_data_send_client.put(
            self._json_safe(self._strip_internal_images(payload))
        )

    @classmethod
    def _strip_internal_images(cls, value):
        """Loại ảnh NumPy nội bộ, giữ overlay và đường dẫn ảnh đã lưu."""
        if isinstance(value, dict):
            return {
                key: cls._strip_internal_images(child)
                for key, child in value.items()
                if key not in {
                    "image",
                    "judgment_image",
                    "inspector_images",
                    "overlay_data",
                }
            }
        if isinstance(value, list):
            return [cls._strip_internal_images(child) for child in value]
        return value

    @staticmethod
    def _json_safe(value):
        """Chuyển payload judgment về kiểu có thể truyền qua Socket.IO."""
        try:
            return json.loads(json.dumps(value, ensure_ascii=False, default=str))
        except (TypeError, ValueError):
            return {"status": "NG", "message": "Payload judgment không hợp lệ."}

    def _session_item_dir(self, prepared, frame_id: str, point_id: str) -> Path:
        """Tạo thư mục lưu dữ liệu của một item trong một session."""
        output_dir = (
            Path(__file__).resolve().parents[1]
            / "output"
            / "judgment"
            / prepared.session_id
            / f"product_{prepared.product_id}"
            / f"frame_{frame_id}"
            / f"item_{point_id}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _save_master_result(self, prepared, frame: dict, point: dict, step: int) -> str:
        """Lưu ảnh master cho item không có cấu hình inspector."""
        output_dir = self._session_item_dir(prepared, frame["frame_id"], point["point_id"])
        source_path = Path(__file__).resolve().parents[1] / str(
            point["source"].get("path_img_point", "")
        ).replace("\\", "/")
        judgment_path = output_dir / "judgment.jpg"
        if source_path.exists():
            shutil.copy2(source_path, judgment_path)
        result = {
            "status": "NO_DATA",
            "overall": False,
            "step": step,
            "number_step": prepared.number_step,
            "message": "Không có dữ liệu master phán định.",
            "inspectors": {},
        }
        (output_dir / "result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._output_url(judgment_path)

    def _save_judgment_result(
        self,
        image,
        prepared,
        frame_id: str,
        point_id: str,
        summary: dict,
    ) -> str:
        """Lưu ảnh gốc, ảnh judgment và JSON kết quả của item."""
        output_dir = self._session_item_dir(prepared, frame_id, point_id)
        original_path = output_dir / "original.jpg"
        judgment_path = output_dir / "judgment.jpg"
        cv2.imwrite(str(original_path), image)
        judgment_image = summary.get("judgment_image")
        if not isinstance(judgment_image, type(image)):
            judgment_image = image
        cv2.imwrite(str(judgment_path), judgment_image)
        inspector_images = summary.get("inspector_images", {})
        inspector_dir = output_dir / "inspectors"
        inspector_image_paths = {}
        if isinstance(inspector_images, dict):
            inspector_dir.mkdir(parents=True, exist_ok=True)
            for inspector_name, inspector_image in inspector_images.items():
                if isinstance(inspector_image, type(image)):
                    inspector_path = inspector_dir / f"{inspector_name}.jpg"
                    cv2.imwrite(str(inspector_path), inspector_image)
                    inspector_image_paths[inspector_name] = self._output_url(inspector_path)
        summary["inspector_image_paths"] = inspector_image_paths
        result_data = {
            key: value for key, value in self._strip_internal_images(summary).items()
        }
        (output_dir / "result.json").write_text(
            json.dumps(result_data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return self._output_url(judgment_path)

    @staticmethod
    def _output_url(path: Path) -> str:
        """Đổi đường dẫn app/output thành URL static cho client."""
        relative = path.relative_to(Path(__file__).resolve().parents[1]).as_posix()
        return f"/output/{relative.removeprefix('output/')}"

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

    def _save_image(self, image, prepared, frame_id: str, point_id: str) -> str:
        """Lưu ảnh point vào app/output và trả về đường dẫn tương đối."""
        output_dir = self._session_item_dir(prepared, frame_id, point_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = output_dir / "original.jpg"
        if not cv2.imwrite(str(image_path), image):
            raise RuntimeError(f"Không lưu được ảnh phán định: {image_path}")
        return self._output_url(image_path)