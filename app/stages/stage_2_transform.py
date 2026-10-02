from app.container import ServiceContainer, EnumMode
from app.core.context import RuntimePipelineState
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any
import queue
import threading
from app.config.path_config import (
    BASE_DIR,
    PATH_FOLDER_OUTPUT_JUDGMENT,
    PATH_FOLDER_OUTPUT,
    URL_PATH_OUTPUT,
)
import cv2
import json
import shutil
import time


@dataclass
class InspectionTaskItem:
    """Đóng gói dữ liệu một điểm đo để chuyển từ luồng chụp sang luồng phán định."""
    prepared: Any
    frame: dict[str, Any]
    point: dict[str, Any]
    step: int
    image: Any = None
    inspectors: dict[str, Any] = field(default_factory=dict)
    active_scale_mm_per_pixel: float = 1.0
    is_calibrated: bool = True
    calibration_reason: str = ""
    is_no_data: bool = False
    no_data_message: str = ""


class StageTransform:
    LINE_BASED_INSPECTORS = {
        "BorderFilmInspector",
        "MeasurementWeldInspector",
        "SlitWeldInspector",
    }

    INSPECTOR_DISPLAY_NAMES = {
        "AirBubblesItemInspector": "Bọt khí đường hàn",
        "MeasurementWeldInspector": "Độ rộng đường hàn",
        "SlitWeldInspector": "Khoảng cách khe hàn",
        "ArmSensorInspector": "ARM Sensor",
        "ArmCoverInspector": "ARM Cover",
        "BorderFilmInspector": "Biên film",
        "MembraneInspector": "Màng bán thấm",
        "HoleItemInspector": "Lỗ thủng",
        "ScratchedPipeItemInspector": "Vết xước ống",
        "EndChippingInspector": "Mẻ đầu ống",
        "ForeignObjectInspector": "Dị vật",
    }

    def __init__(self, services: ServiceContainer, queue_maxsize: int = 3):
        self.services = services
        self.queue_maxsize = max(1, int(queue_maxsize))

    def run(self):
        """Di chuyển, chụp ảnh và phán định toàn bộ point của sản phẩm theo mô hình Pipelined Queue.

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
        results: list[dict[str, Any]] = []
        consumer_errors: list[Exception] = []

        self._send_client({
            "type": "judgment_reset",
            "data": {
                "product_id": prepared.product_id,
                "number_step": prepared.number_step,
                "session_id": prepared.session_id,
            },
        })

        inspection_queue: queue.Queue[InspectionTaskItem | None] = queue.Queue(
            maxsize=self.queue_maxsize
        )

        consumer_thread = threading.Thread(
            target=self._consumer_worker,
            args=(inspection_queue, results, consumer_errors),
            daemon=True,
            name="Stage2JudgerWorker",
        )
        consumer_thread.start()

        try:
            # Luồng Producer: Điều khiển di chuyển IAI, chụp ảnh và đẩy task vào queue
            self._producer_loop(prepared, inspection_queue, consumer_errors)

            # Chờ Consumer worker hoàn tất toàn bộ task trong queue
            consumer_thread.join()

            if consumer_errors:
                raise consumer_errors[0]

            # Sắp xếp lại danh sách kết quả theo đúng thứ tự step trước khi tổng hợp
            results.sort(key=lambda r: int(r.get("step", 0)))

            self.services.runtime_state.set_product_result(results)
            is_overall_ok = all(result.get("overall") is True for result in results)
            counts = self.services.obj_product_count_service.record_result(is_overall_ok)
            self._send_client({
                "type": "judgment_product_result",
                "data": {
                    "product_id": prepared.product_id,
                    "session_id": prepared.session_id,
                    "number_step": prepared.number_step,
                    "overall": is_overall_ok,
                    "status": "OK" if is_overall_ok else "NG",
                    "items": results,
                    "counts": counts,
                },
            })
            self.services.set_mode(EnumMode.MODE_EXPORT)
            return results
        except Exception as error:
            # Dừng consumer thread an toàn nếu có lỗi ở producer hoặc consumer
            try:
                inspection_queue.put_nowait(None)
            except (queue.Full, Exception):
                pass
            if consumer_thread.is_alive():
                consumer_thread.join(timeout=1.0)

            results.sort(key=lambda r: int(r.get("step", 0)))
            counts = self.services.obj_product_count_service.record_result(False)
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
                    "counts": counts,
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

    def _producer_loop(
        self,
        prepared: Any,
        inspection_queue: queue.Queue,
        consumer_errors: list[Exception],
    ) -> None:
        """Luồng Producer: Di chuyển IAI và trigger chụp ảnh, đẩy vào hàng đợi."""
        step = 0
        try:
            for frame in prepared.frames:
                for point in frame["points"]:
                    self._ensure_running()
                    if consumer_errors:
                        raise consumer_errors[0]

                    step += 1
                    task = self._capture_point_task(prepared, frame, point, step)
                    self._enqueue_task(inspection_queue, task, consumer_errors)

            # Sau khi chụp xong toàn bộ point, lập tức đưa IAI về vị trí item đầu tiên (step 1)
            self._return_iai_to_start(prepared)

            # Gửi tín hiệu hoàn tất (sentinel) cho consumer worker
            self._enqueue_task(inspection_queue, None, consumer_errors)
        except Exception:
            try:
                inspection_queue.put_nowait(None)
            except (queue.Full, Exception):
                pass
            raise

    def _enqueue_task(
        self,
        inspection_queue: queue.Queue,
        task: InspectionTaskItem | None,
        consumer_errors: list[Exception],
    ) -> None:
        """Đưa task vào queue, hỗ trợ backpressure chặn luồng chụp tạm thời khi queue đầy."""
        while not self.services.runtime_state.is_stop_requested():
            if consumer_errors:
                raise consumer_errors[0]
            try:
                inspection_queue.put(task, timeout=0.2)
                return
            except queue.Full:
                continue
        if self.services.runtime_state.is_stop_requested():
            raise RuntimeError("Pipeline đã nhận yêu cầu dừng trong khi chờ hàng đợi phán định")

    def _return_iai_to_start(self, prepared: Any) -> None:
        """Đưa IAI về vị trí item đầu tiên (step 1) hoặc vị trí 0,0,0."""
        first_point = None
        if prepared.frames and prepared.frames[0].get("points"):
            first_point = prepared.frames[0]["points"][0]

        if first_point is not None:
            first_frame_id = prepared.frames[0].get("frame_id", "0")
            first_point_id = first_point.get("point_id", "0")
            first_point_target = {
                "frame_id": first_frame_id,
                "point_id": first_point_id,
                "x": first_point["x"],
                "y": first_point["y"],
                "z": first_point["z"],
            }
            print(
                f"[STAGE2] Hoàn tất chụp ảnh các điểm, đưa IAI về vị trí item đầu tiên "
                f"(step 1: frame={first_frame_id}, item={first_point_id}) "
                f"tại X={first_point['x']}, Y={first_point['y']}, Z={first_point['z']}"
            )
            self.services.send_judgment_log(
                f"🔄 Đưa IAI về vị trí item đầu tiên (step 1: frame {first_frame_id}, point {first_point_id})."
            )
            if not self._move_with_retry(first_point_target):
                raise RuntimeError(
                    f"IAI không về được vị trí item đầu tiên (step 1: frame {first_frame_id}, point {first_point_id}) sau sản phẩm"
                )
        else:
            if not self.services.obj_iai_control.move_to_point(0, 0, 0):
                raise RuntimeError("IAI không về được vị trí 0,0,0 sau sản phẩm")

    def _capture_point_task(
        self,
        prepared: Any,
        frame: dict[str, Any],
        point: dict[str, Any],
        step: int,
    ) -> InspectionTaskItem:
        """Thực hiện di chuyển và chụp ảnh tại một điểm, đóng gói thành task cho hàng đợi."""
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
            return InspectionTaskItem(
                prepared=prepared,
                frame=frame,
                point=point,
                step=step,
                inspectors={},
                is_no_data=True,
                no_data_message="Không có dữ liệu master phán định.",
            )

        frame_calibration = frame.get("calibration")
        if not isinstance(frame_calibration, dict):
            frame_calibration_map = getattr(prepared, "frame_calibrations", {})
            if not isinstance(frame_calibration_map, dict):
                frame_calibration_map = {}
            frame_calibration = frame_calibration_map.get(str(frame_id), {})
        scale_mm_per_pixel = frame_calibration.get("scale_mm_per_pixel")
        is_calibrated = bool(frame_calibration.get("is_calibrated"))
        calibration_reason = str(
            frame_calibration.get("reason")
            or "Frame chưa có calibration hợp lệ."
        )

        requires_calibration = self._requires_calibration(inspectors)

        if requires_calibration and not is_calibrated:
            no_data_message = (
                f"Thiếu calibration cho frame {frame_id}. {calibration_reason}"
            )
            self.services.send_judgment_log(
                f"⚠️ Frame {frame_id}, point {point_id}: {no_data_message}"
            )
            return InspectionTaskItem(
                prepared=prepared,
                frame=frame,
                point=point,
                step=step,
                inspectors={},
                is_no_data=True,
                no_data_message=no_data_message,
            )

        if requires_calibration:
            if not isinstance(scale_mm_per_pixel, (int, float)) or float(scale_mm_per_pixel) <= 0:
                raise RuntimeError(
                    f"Frame {frame_id} có scale_mm_per_pixel không hợp lệ: {scale_mm_per_pixel}"
                )
            active_scale_mm_per_pixel = float(scale_mm_per_pixel)
        else:
            fallback_scale = getattr(prepared, "scale_mm_per_pixel", 1.0)
            if not isinstance(fallback_scale, (int, float)) or float(fallback_scale) <= 0:
                fallback_scale = 1.0
            active_scale_mm_per_pixel = float(fallback_scale)

        print(f"[STAGE2] Di chuyển IAI đến frame={frame_id}, item={point_id}: {point['x']},{point['y']},{point['z']}")
        if not self._move_with_retry(point):
            raise RuntimeError(f"IAI di chuyển thất bại tại frame {frame_id}, point {point_id}")
        image = self._capture_with_retry()
        print(f"[STAGE2] Đã chụp ảnh frame={frame_id}, item={point_id}; đẩy vào hàng đợi phán định.")

        return InspectionTaskItem(
            prepared=prepared,
            frame=frame,
            point=point,
            step=step,
            image=image,
            inspectors=inspectors,
            active_scale_mm_per_pixel=active_scale_mm_per_pixel,
            is_calibrated=is_calibrated,
            calibration_reason=calibration_reason,
            is_no_data=False,
        )

    def _consumer_worker(
        self,
        inspection_queue: queue.Queue,
        results: list[dict[str, Any]],
        consumer_errors: list[Exception],
    ) -> None:
        """Luồng Consumer Worker: lấy ảnh từ hàng đợi, thực thi Judment.run_summary và gửi Socket.IO."""
        while not self.services.runtime_state.is_stop_requested():
            try:
                task = inspection_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if task is None:
                inspection_queue.task_done()
                break

            try:
                if task.is_no_data:
                    result = self._handle_no_data_task(task)
                else:
                    result = self._execute_judgment_task(task)
                results.append(result)
                self._send_client({"type": "judgment_item_result", "data": result})
            except Exception as error:
                result = {
                    "product_id": task.prepared.product_id,
                    "frame_id": task.frame["frame_id"],
                    "item_id": task.point["point_id"],
                    "session_id": task.prepared.session_id,
                    "status": "ERROR",
                    "overall": False,
                    "number_step": task.prepared.number_step,
                    "step": task.step,
                    "inspectors": {},
                    "message": str(error),
                }
                results.append(result)
                self._send_client({"type": "judgment_item_result", "data": result})
                consumer_errors.append(error)
                break
            finally:
                inspection_queue.task_done()

    def _handle_no_data_task(self, task: InspectionTaskItem) -> dict[str, Any]:
        """Xử lý item NO_DATA (không có cấu hình hoặc thiếu calibration)."""
        judgment_path = self._save_no_data_result(
            task.prepared,
            task.frame,
            task.point,
            task.step,
            task.no_data_message,
        )
        return {
            "product_id": task.prepared.product_id,
            "frame_id": task.frame["frame_id"],
            "item_id": task.point["point_id"],
            "session_id": task.prepared.session_id,
            "status": "NO_DATA",
            "overall": False,
            "number_step": task.prepared.number_step,
            "step": task.step,
            "judgment_path": judgment_path,
            "inspectors": {},
            "message": task.no_data_message,
        }

    def _execute_judgment_task(self, task: InspectionTaskItem) -> dict[str, Any]:
        """Thực thi phán định AI trên ảnh đã chụp từ queue."""
        frame_id = task.frame["frame_id"]
        point_id = task.point["point_id"]
        image = task.image

        print(f"[STAGE2][WORKER] Bắt đầu Judment.run_summary cho frame={frame_id}, item={point_id}, step={task.step}")
        image_path = self._save_image(image, task.prepared, frame_id, point_id)
        raw_summary = self.services.obj_judment.run_summary(
            image=image,
            inspectors=task.inspectors,
            scale_mm_per_pixel=task.active_scale_mm_per_pixel,
            training_context={
                "session_id": task.prepared.session_id,
                "product_id": task.prepared.product_id,
                "frame_id": frame_id,
                "item_id": point_id,
            },
        )
        summary = dict(raw_summary) if isinstance(raw_summary, dict) else {}
        summary["inspectors"] = {
            k: dict(v) if isinstance(v, dict) else v
            for k, v in summary.get("inspectors", {}).items()
        }
        print(
            f"[STAGE2][WORKER] Kết thúc phán định frame={frame_id}, item={point_id}: "
            f"status={summary.get('status')}, overall={summary.get('overall')}"
        )
        for inspector_name, inspector_result in summary.get("inspectors", {}).items():
            inspector_result["display_name"] = self.INSPECTOR_DISPLAY_NAMES.get(
                inspector_name,
                inspector_name,
            )
        judgment_path = self._output_url(
            self._session_item_dir(task.prepared, frame_id, point_id) / "judgment.jpg"
        )
        summary.update({
            "product_id": task.prepared.product_id,
            "frame_id": frame_id,
            "point_id": point_id,
            "item_id": point_id,
            "session_id": task.prepared.session_id,
            "number_step": task.prepared.number_step,
            "step": task.step,
            "iai": {key: task.point[key] for key in ("x", "y", "z")},
            "calibration": {
                "is_calibrated": task.is_calibrated,
                "scale_mm_per_pixel": task.active_scale_mm_per_pixel,
                "reason": task.calibration_reason,
            },
            "judgment_path": judgment_path,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        })
        judgment_path = self._save_judgment_result(
            image,
            task.prepared,
            frame_id,
            point_id,
            summary,
        )
        summary["judgment_path"] = judgment_path

        # Ghi log judgment theo chuẩn: chỉ ghi khi có hạng mục NG
        ng_errors: list[str] = []
        for inspector_name, inspector_result in summary.get("inspectors", {}).items():
            if inspector_result.get("ok") is False:
                errs = inspector_result.get("errors")
                if errs and isinstance(errs, list):
                    for err in errs:
                        err_str = str(err).strip()
                        if not err_str.startswith("🔵"):
                            err_str = f"🔵{err_str}"
                        ng_errors.append(err_str)
                else:
                    msg = inspector_result.get("message") or "Không đạt chuẩn"
                    display_name = inspector_result.get("display_name", inspector_name)
                    ng_errors.append(
                        f"🔵[{display_name}] NG - \"{display_name}\" - Quy định:\"Đạt chuẩn\" - Thực tế :\"{msg}\""
                    )

        if ng_errors:
            log_lines = [f"🔻Frame: {frame_id} Ảnh thứ: {point_id}"]
            log_lines.extend(ng_errors)
            self.services.send_judgment_log("\n".join(log_lines))

        return summary

    def _process_point(
        self,
        prepared: Any,
        frame: dict[str, Any],
        point: dict[str, Any],
        step: int,
    ) -> dict[str, Any]:
        """Tương thích ngược: Xử lý đồng bộ một point (chụp và phán định trực tiếp)."""
        task = self._capture_point_task(prepared, frame, point, step)
        if task.is_no_data:
            return self._handle_no_data_task(task)
        return self._execute_judgment_task(task)

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
            PATH_FOLDER_OUTPUT_JUDGMENT
            / prepared.session_id
            / f"product_{prepared.product_id}"
            / f"frame_{frame_id}"
            / f"item_{point_id}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _save_no_data_result(
        self,
        prepared,
        frame: dict,
        point: dict,
        step: int,
        message: str,
    ) -> str:
        """Lưu ảnh tham chiếu và result NO_DATA cho item chưa đủ dữ liệu chạy.

        Input: Dữ liệu prepared/frame/point, thứ tự step và nội dung message.
        Output: URL ảnh judgment đã lưu (copy từ ảnh point master nếu có).
        Errors: Không phát sinh; thiếu ảnh nguồn vẫn tạo ``result.json`` NO_DATA.
        """
        output_dir = self._session_item_dir(prepared, frame["frame_id"], point["point_id"])
        source_path = BASE_DIR / str(
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
            "message": message,
            "inspectors": {},
        }
        (output_dir / "result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._output_url(judgment_path)

    def _requires_calibration(self, inspectors: dict[str, Any]) -> bool:
        """Xác định item có chứa hạng mục đo cần calibration theo frame hay không.

        Input: Dict config inspector của một item trong judgment law.
        Output: ``True`` nếu item có Measurement/Slit/Border với cấu hình hợp lệ.
        Errors: Không phát sinh; dữ liệu sai kiểu được bỏ qua an toàn.
        """
        if not isinstance(inspectors, dict):
            return False
        for inspector_name in self.LINE_BASED_INSPECTORS:
            inspector_config = inspectors.get(inspector_name)
            if isinstance(inspector_config, dict) and inspector_config:
                return True
        return False

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
        relative = path.relative_to(PATH_FOLDER_OUTPUT).as_posix()
        return f"{URL_PATH_OUTPUT}/{relative}"

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