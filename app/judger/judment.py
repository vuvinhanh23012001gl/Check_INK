from dataclasses import dataclass, field
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Sequence
import numpy as np
import cv2
from .base_ai import BaseJudgerAI, JudgmentResult


@dataclass
class InspectorTask:
    """Cấu hình một inspector trong một lần kiểm tra ảnh.
    Input:
        inspector: Instance của một lớp kế thừa ``BaseJudgerAI``.
        standard_data: Dữ liệu chuẩn truyền vào ``compare``.
        define_args: Tham số vị trí truyền thêm cho ``define`` sau ảnh.
        define_kwargs: Tham số tên truyền vào ``define``.
        compare_kwargs: Tham số tên truyền thêm vào ``compare``.
    Output:
        Một cấu hình có thể được ``Judment`` thực thi tuần tự.
    Errors:
        ``TypeError`` nếu ``inspector`` không phải là ``BaseJudgerAI``.
    """
    inspector: BaseJudgerAI
    standard_data: Any
    define_args: tuple[Any, ...] = ()
    define_kwargs: dict[str, Any] = field(default_factory=dict)
    compare_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Kiểm tra inspector ngay khi tạo task.

        Input: Không có ngoài dữ liệu đã truyền vào constructor.
        Output: Không trả về dữ liệu.
        Errors: ``TypeError`` nếu task chứa object không phải judger hợp lệ.
        """
        if not isinstance(self.inspector, BaseJudgerAI):
            raise TypeError("inspector phải là instance của BaseJudgerAI")


class Judment:
    """Điều phối toàn bộ inspector trên cùng một ảnh đầu vào.

    Mỗi task được chạy theo thứ tự xuất hiện trong mảng: ``define`` ->
    ``compare`` -> ``judge``.  Ảnh được truyền vào ``define`` của từng task;
    các detector tự quyết định ROI và cách nhận diện riêng của mình.
    """

    def __init__(
        self,
        inspector_registry: Mapping[str, BaseJudgerAI] | None = None,
    ) -> None:
        """Khởi tạo bộ điều phối với registry các detector đã load model.

        Input:
            inspector_registry: Mapping từ tên inspector trong JSON đến
                instance detector tương ứng.
        Output: Không trả về dữ liệu.
        Errors: ``TypeError`` nếu registry chứa detector không hợp lệ.
        """
        self.inspector_registry = dict(inspector_registry or {})
        for name, inspector in self.inspector_registry.items():
            if not isinstance(name, str) or not isinstance(inspector, BaseJudgerAI):
                raise TypeError("inspector_registry phải map tên tới BaseJudgerAI")

    def run(
        self,
        image: np.ndarray,
        inspectors: Sequence[InspectorTask] | Mapping[str, Any],
        inspector_registry: Mapping[str, BaseJudgerAI] | None = None,
        scale_mm_per_pixel: float = 1.0,
    ) -> dict[str, JudgmentResult]:
        """Chạy lần lượt tất cả inspector trên một ảnh.

        Input:
            image: Ảnh NumPy không được rỗng.
            inspectors: Mảng ``InspectorTask`` hoặc object cấu hình judgment
                dạng ``{InspectorName: config}``.
            inspector_registry: Registry tùy chọn, dùng khi ``inspectors`` là
                object JSON; nếu bỏ qua sẽ dùng registry trong constructor.
            scale_mm_per_pixel: Hệ số calibration dùng cho Border khi config
                không truyền task thủ công.
        Output:
            Dictionary có key là ``INSPECTOR_NAME`` và value là
            ``JudgmentResult`` tương ứng.
        Errors:
            ``ValueError`` nếu ảnh rỗng, cấu hình rỗng, trùng tên hoặc config
                chứa inspector chưa được triển khai.
            ``TypeError`` nếu phần tử trong mảng không phải ``InspectorTask``.
            Lỗi từ detector được truyền ra ngoài để caller biết chính xác
            inspector nào không xử lý được dữ liệu.
        """
        if not isinstance(image, np.ndarray) or image.size == 0:
            raise ValueError("image đầu vào không được rỗng")
        if not inspectors:
            raise ValueError("inspectors phải chứa ít nhất một inspector")
        if not isinstance(scale_mm_per_pixel, (int, float)) or scale_mm_per_pixel <= 0:
            raise ValueError("scale_mm_per_pixel phải là số lớn hơn 0")

        if isinstance(inspectors, Mapping):
            registry = dict(inspector_registry or self.inspector_registry)
            inspectors = self._tasks_from_config(
                inspectors,
                registry,
                float(scale_mm_per_pixel),
            )

        results: dict[str, JudgmentResult] = {}
        for index, task in enumerate(inspectors, start=1):
            if not isinstance(task, InspectorTask):
                raise TypeError("mọi phần tử inspectors phải là InspectorTask")
            name = task.inspector.get_inspector_name()
            if name in results:
                raise ValueError(f"Inspector bị trùng tên: {name}")
            self._log_inspector_start(index, name, image, task)
            runtime_data = task.inspector.define(
                image,
                *task.define_args,
                **task.define_kwargs,
            )
            comparison_data = task.inspector.compare(
                task.standard_data,
                runtime_data,
                **task.compare_kwargs,
            )
            result = task.inspector.judge(comparison_data)
            if not isinstance(result, JudgmentResult):
                raise TypeError(f"{name}.judge() phải trả về JudgmentResult")
            results[name] = result
            self._log_inspector_result(name, runtime_data, comparison_data, result)
        return results

    @staticmethod
    def _tasks_from_config(
        config: Mapping[str, Any],
        inspector_registry: Mapping[str, BaseJudgerAI],
        scale_mm_per_pixel: float,
    ) -> list[InspectorTask]:
        """Chuyển object config thành danh sách task có thể thực thi.

        Input:
            config: Object judgment của một frame, key là tên inspector.
            inspector_registry: Detector đã khởi tạo theo từng tên key.
        Output: Danh sách ``InspectorTask`` theo thứ tự config.
        Errors: ``ValueError`` nếu config inspector chưa có detector hoặc
            dữ liệu ROI/line không đúng cấu trúc.
        """
        tasks: list[InspectorTask] = []
        for name, inspector_config in config.items():
            inspector = inspector_registry.get(name)
            if inspector is None:
                raise ValueError(
                    f"Chưa có detector cho inspector '{name}'"
                )
            if not isinstance(inspector_config, Mapping):
                raise ValueError(f"Cấu hình {name} phải là object")

            if name in {
                "BorderFilmInspector",
                "MeasurementWeldInspector",
                "SlitWeldInspector",
            }:
                lines = []
                for line in inspector_config.values():
                    if not isinstance(line, Mapping):
                        raise ValueError(f"Cấu hình line của {name} không hợp lệ")
                    try:
                        lines.append((
                            float(line["xStart"]),
                            float(line["yStart"]),
                            float(line["xEnd"]),
                            float(line["yEnd"]),
                        ))
                    except (KeyError, TypeError, ValueError) as error:
                        raise ValueError(f"Cấu hình line của {name} thiếu tọa độ") from error
                tasks.append(
                    InspectorTask(
                        inspector=inspector,
                        standard_data={name: dict(inspector_config)},
                        define_args=(lines,),
                        compare_kwargs={
                            "scale_mm_per_pixel": scale_mm_per_pixel
                        },
                    )
                )
                continue

            if name == "AirBubblesItemInspector":
                regions = []
                for region in inspector_config.values():
                    if not isinstance(region, Mapping):
                        raise ValueError(f"Cấu hình vùng của {name} không hợp lệ")
                    try:
                        x1 = int(region["xStart"])
                        y1 = int(region["yStart"])
                        x2 = int(region["xEnd"])
                        y2 = int(region["yEnd"])
                    except (KeyError, TypeError, ValueError) as error:
                        raise ValueError(f"Cấu hình vùng của {name} thiếu tọa độ") from error
                    if x2 <= x1 or y2 <= y1:
                        raise ValueError(f"Cấu hình vùng của {name} có kích thước không hợp lệ")
                    regions.append((x1, y1, x2 - x1, y2 - y1))
                tasks.append(
                    InspectorTask(
                        inspector=inspector,
                        standard_data=True,
                        define_args=(regions,),
                    )
                )
                continue

            try:
                x1 = int(inspector_config["xStart"])
                y1 = int(inspector_config["yStart"])
                x2 = int(inspector_config["xEnd"])
                y2 = int(inspector_config["yEnd"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Cấu hình ROI của {name} thiếu tọa độ") from error

            define_args: tuple[Any, ...] = (x1, y1, x2, y2)
            tasks.append(
                InspectorTask(
                    inspector=inspector,
                    standard_data=True,
                    define_args=define_args,
                )
            )
        return tasks

    def evaluate(
        self,
        image: np.ndarray,
        inspectors: Sequence[InspectorTask] | Mapping[str, Any],
        inspector_registry: Mapping[str, BaseJudgerAI] | None = None,
        scale_mm_per_pixel: float = 1.0,
    ) -> dict[str, JudgmentResult]:
        """Alias dễ đọc hơn cho ``run``.

        Input: Giống ``run``.
        Output: Dictionary kết quả theo tên inspector.
        Errors: Giống ``run``.
        """
        return self.run(
            image,
            inspectors,
            inspector_registry,
            scale_mm_per_pixel,
        )

    def run_summary(
        self,
        image: np.ndarray,
        inspectors: Sequence[InspectorTask] | Mapping[str, Any],
        inspector_registry: Mapping[str, BaseJudgerAI] | None = None,
        scale_mm_per_pixel: float = 1.0,
    ) -> dict[str, Any]:
        """Chạy toàn bộ tool trên một ảnh và tạo output tổng để ghi log.

        Input:
            image: Ảnh NumPy cần kiểm tra.
            inspectors: Danh sách task hoặc cấu hình judgment theo JSON.
            inspector_registry: Registry detector, dùng khi inspectors là JSON.
            scale_mm_per_pixel: Hệ số calibration truyền cho detector đo lường.
        Output:
            Dict gồm ``overall``, ``status``, ``inspectors``, ``errors``,
            ``message`` và metadata kích thước/thời điểm xử lý. Mỗi inspector
            chứa đầy đủ output của ``JudgmentResult.to_dict()``.
        Errors:
            ``ValueError`` nếu ảnh, config hoặc registry không hợp lệ. Lỗi của
            từng detector được ghi thành kết quả NG của tool đó để các tool
            còn lại vẫn tiếp tục được xử lý.
        """
        if not isinstance(image, np.ndarray) or image.size == 0:
            raise ValueError("image đầu vào không được rỗng")
        tasks = inspectors
        if isinstance(inspectors, Mapping):
            registry = dict(inspector_registry or self.inspector_registry)
            tasks = self._tasks_from_config(
                inspectors,
                registry,
                float(scale_mm_per_pixel),
            )
        if not tasks:
            raise ValueError("inspectors phải chứa ít nhất một inspector")

        inspector_results: dict[str, dict[str, Any]] = {}
        errors: list[dict[str, str]] = []
        inspector_images: dict[str, np.ndarray] = {}
        overlay_data: dict[str, dict[str, Any]] = {}
        judgment_image = image.copy()
        for index, task in enumerate(tasks, start=1):
            if not isinstance(task, InspectorTask):
                raise TypeError("mọi phần tử inspectors phải là InspectorTask")
            name = task.inspector.get_inspector_name()
            self._log_inspector_start(index, name, image, task)
            try:
                runtime_data = task.inspector.define(
                    image,
                    *task.define_args,
                    **task.define_kwargs,
                )
                comparison_data = task.inspector.compare(
                    task.standard_data,
                    runtime_data,
                    **task.compare_kwargs,
                )
                result = task.inspector.judge(comparison_data)
                if not isinstance(result, JudgmentResult):
                    raise TypeError("detector phải trả về JudgmentResult")
                inspector_results[name] = result.to_dict()
                inspector_image, inspector_overlay = self._render_inspector_overlay(
                    image,
                    name,
                    task.standard_data,
                    task.define_args,
                    runtime_data,
                    comparison_data,
                    result,
                )
                inspector_images[name] = inspector_image
                overlay_data[name] = inspector_overlay
                judgment_image = self._blend_overlay_image(judgment_image, inspector_image)
                self._log_inspector_result(name, runtime_data, comparison_data, result)
                if not result.ok:
                    errors.append({
                        "inspector": name,
                        "message": result.message or "Tool phán định NG",
                    })
            except Exception as error:
                message = str(error)
                print(f"[JUDMENT][{name}] ERROR: {message}")
                errors.append({"inspector": name, "message": message})
                inspector_results[name] = JudgmentResult(
                    ok=False,
                    status="NG",
                    message=f"Lỗi tool {name}: {message}",
                    errors=[message],
                ).to_dict()

        overall = not errors and all(
            result.get("ok") is True for result in inspector_results.values()
        )
        return {
            "overall": overall,
            "status": "OK" if overall else "NG",
            "message": (
                "Tất cả hạng mục kiểm tra đạt"
                if overall
                else f"Có {len(errors)} hạng mục kiểm tra không đạt"
            ),
            "image": {
                "height": int(image.shape[0]),
                "width": int(image.shape[1]),
                "channels": int(image.shape[2]) if image.ndim == 3 else 1,
            },
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "inspectors": inspector_results,
            "errors": errors,
            "overlay_data": overlay_data,
            "judgment_image": judgment_image,
            "inspector_images": inspector_images,
        }

    @staticmethod
    def _blend_overlay_image(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
        """Gộp ảnh overlay inspector lên ảnh judgment tổng."""
        if not isinstance(overlay, np.ndarray) or overlay.shape != base.shape:
            return base
        return cv2.addWeighted(base, 0.55, overlay, 0.45, 0)

    @classmethod
    def _render_inspector_overlay(
        cls,
        image: np.ndarray,
        name: str,
        standard_data: Any,
        define_args: tuple[Any, ...],
        runtime_data: Any,
        comparison_data: Any,
        result: JudgmentResult,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Vẽ cấu hình chuẩn và dữ liệu runtime theo đúng loại inspector.

        Input: Ảnh gốc, tên inspector, cấu hình chuẩn, dữ liệu runtime/so
            sánh và kết quả phán định của một tool.
        Output: Tuple gồm ảnh overlay và metadata các line, khung, polygon
            đã vẽ. Line đo chỉ được vẽ là line có nhãn, còn cấu hình vùng
            được vẽ thành rectangle có nhãn.
        Errors: Không phát sinh với cấu hình không đầy đủ; các phần tử không
            có đủ tọa độ sẽ được bỏ qua.
        """
        runtime_source = runtime_data if isinstance(runtime_data, dict) else {}
        comparison_source = comparison_data if isinstance(comparison_data, dict) else {}
        runtime_image = runtime_source.get("image")
        if not isinstance(runtime_image, np.ndarray):
            runtime_image = comparison_source.get("image")
        output = runtime_image.copy() if isinstance(runtime_image, np.ndarray) else image.copy()
        overlay: dict[str, Any] = {"standard": {}, "runtime": {}, "status": result.status}
        config = standard_data.get(name, standard_data) if isinstance(standard_data, dict) else standard_data

        if isinstance(config, dict):
            for config_key, value in config.items():
                if not isinstance(value, dict):
                    continue
                coordinate_keys = ("xStart", "yStart", "xEnd", "yEnd")
                if not all(key in value for key in coordinate_keys):
                    continue
                shape = [
                        int(value["xStart"]), int(value["yStart"]),
                        int(value["xEnd"]), int(value["yEnd"]),
                ]
                is_measurement_line = any(
                    key in value
                    for key in ("level1", "level2", "level3", "level4", "level5", "widthMin", "widthMax")
                )
                label = str(
                    value.get("name_line")
                    or value.get("nameLine")
                    or value.get("name")
                    or config_key
                )
                if is_measurement_line:
                    cv2.line(
                        output,
                        (shape[0], shape[1]),
                        (shape[2], shape[3]),
                        (255, 200, 0),
                        2,
                    )
                    cls._draw_overlay_label(output, label, shape[0], shape[1], (255, 200, 0))
                    overlay["standard"].setdefault("lines", []).append(shape)
                else:
                    cv2.rectangle(
                        output,
                        (shape[0], shape[1]),
                        (shape[2], shape[3]),
                        (255, 200, 0),
                        2,
                    )
                    cls._draw_overlay_label(output, label, shape[0], shape[1], (255, 200, 0))
                    overlay["standard"].setdefault("boxes", []).append(shape)
        elif name == "AirBubblesItemInspector" and define_args:
            regions = define_args[0]
            for region in regions if isinstance(regions, list) else []:
                if len(region) != 4:
                    continue
                x, y, width, height = [int(value) for value in region]
                box = [x, y, x + width, y + height]
                cv2.rectangle(output, (x, y), (x + width, y + height), (255, 200, 0), 2)
                overlay["standard"].setdefault("boxes", []).append(box)
        elif standard_data is True and len(define_args) == 4:
            x1, y1, x2, y2 = [int(value) for value in define_args]
            cv2.rectangle(output, (x1, y1), (x2, y2), (255, 200, 0), 2)
            overlay["standard"].setdefault("boxes", []).append([x1, y1, x2, y2])

        polygon = runtime_source.get("polygon")
        if polygon is None:
            polygon = comparison_source.get("polygon")
        if polygon is not None:
            polygon_points = cls._points_array(polygon)
            if polygon_points is not None and len(polygon_points) >= 3:
                cv2.polylines(output, [polygon_points], True, (0, 255, 0), 3)
                overlay["runtime"]["polygons"] = [polygon_points.reshape(-1, 2).tolist()]

        lines = []
        for item in comparison_source.get("comparisons", []):
            runtime_line = item.get("runtime") if isinstance(item, dict) else None
            original_line = runtime_line.get("original_line") if isinstance(runtime_line, dict) else None
            if original_line and len(original_line) == 4:
                lines.append([float(value) for value in original_line])
                is_valid = bool(item.get("is_valid"))
                color = (0, 255, 0) if is_valid else (0, 0, 255)
                cv2.line(
                    output,
                    (int(original_line[0]), int(original_line[1])),
                    (int(original_line[2]), int(original_line[3])),
                    color,
                    3,
                )
                for point_key in ("intersection_point_1", "intersection_point_2"):
                    point = runtime_line.get(point_key)
                    if point and len(point) == 2:
                        cv2.circle(output, (int(point[0]), int(point[1])), 6, (255, 0, 0), -1)
        if lines:
            overlay["runtime"]["lines"] = lines

        objects = runtime_source.get("objects") or comparison_source.get("objects")
        if isinstance(objects, list):
            boxes = []
            for obj in objects:
                if not isinstance(obj, dict):
                    continue
                box = obj.get("box") or obj.get("bbox")
                if isinstance(box, (list, tuple)) and len(box) == 4:
                    x1, y1, x2, y2 = [int(float(value)) for value in box]
                    cv2.rectangle(output, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    boxes.append([x1, y1, x2, y2])
            if boxes:
                overlay["runtime"]["boxes"] = boxes

        return output, overlay

    @staticmethod
    def _draw_overlay_label(
        image: np.ndarray,
        label: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        """Vẽ nhãn ngắn, dễ đọc tại góc trên-trái của line hoặc rectangle.

        Input: Ảnh OpenCV, nội dung nhãn, tọa độ neo và màu BGR.
        Output: Không trả về; nhãn được vẽ trực tiếp lên ``image``.
        Errors: Không phát sinh; nhãn rỗng được thay bằng chuỗi mặc định.
        """
        text = label.strip() or "Unnamed"
        origin = (max(0, int(x)), max(16, int(y) - 6))
        cv2.putText(
            image,
            text,
            origin,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )

    @staticmethod
    def _points_array(value: Any) -> np.ndarray | None:
        """Chuẩn hóa polygon về mảng OpenCV dạng Nx1x2."""
        try:
            array = np.asarray(value, dtype=np.float32).reshape(-1, 1, 2)
            return array.astype(np.int32)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _log_inspector_start(
        index: int,
        name: str,
        image: np.ndarray,
        task: InspectorTask,
    ) -> None:
        """In log đầy đủ trước khi gọi model của một inspector.

        Input: Thứ tự, tên inspector, ảnh đầu vào và task tương ứng.
        Output: Không trả về; ghi thông tin ra console.
        Errors: Không phát sinh.
        """
        print(f"[JUDMENT][{index}] START {name}")
        print(
            f"[JUDMENT][{name}] image_shape={image.shape}, "
            f"dtype={image.dtype}"
        )
        print(f"[JUDMENT][{name}] standard_data={Judment._format_log_data(task.standard_data)}")
        print(f"[JUDMENT][{name}] define_args={Judment._format_log_data(task.define_args)}")
        print(f"[JUDMENT][{name}] define_kwargs={Judment._format_log_data(task.define_kwargs)}")
        print(f"[JUDMENT][{name}] compare_kwargs={Judment._format_log_data(task.compare_kwargs)}")

    @staticmethod
    def _log_inspector_result(
        name: str,
        runtime_data: Any,
        comparison_data: Any,
        result: JudgmentResult,
    ) -> None:
        """In log runtime, comparison và kết luận của một inspector.

        Input: Tên inspector và dữ liệu trả về từ ba bước xử lý.
        Output: Không trả về; ghi đầy đủ trạng thái ra console.
        Errors: Không phát sinh.
        """
        print(f"[JUDMENT][{name}] runtime_data={Judment._format_log_data(runtime_data)}")
        print(f"[JUDMENT][{name}] comparison_data={Judment._format_log_data(comparison_data)}")
        print(
            f"[JUDMENT][{name}] END status={result.status}, "
            f"ok={result.ok}, message={result.message}, errors={result.errors}"
        )

    @staticmethod
    def _format_log_data(value: Any) -> Any:
        """Rút gọn mảng NumPy khi ghi log nhưng giữ nguyên cấu trúc dữ liệu.

        Input: Giá trị bất kỳ trong task hoặc kết quả detector.
        Output: Giá trị có thể in an toàn, ảnh được thay bằng shape/dtype.
        Errors: Không phát sinh.
        """
        if isinstance(value, np.ndarray):
            return f"<numpy shape={value.shape} dtype={value.dtype}>"
        if isinstance(value, dict):
            return {
                key: Judment._format_log_data(child)
                for key, child in value.items()
            }
        if isinstance(value, list):
            return [Judment._format_log_data(child) for child in value]
        if isinstance(value, tuple):
            return tuple(Judment._format_log_data(child) for child in value)
        return value

    def judge_image(
        self,
        image: np.ndarray,
        inspectors: Sequence[InspectorTask] | Mapping[str, Any],
        inspector_registry: Mapping[str, BaseJudgerAI] | None = None,
        scale_mm_per_pixel: float = 1.0,
    ) -> dict[str, Any]:
        """Tên gọi thay thế cho ``run_summary`` dành cho luồng production.

        Input, output và lỗi: Giống ``run_summary``.
        """
        return self.run_summary(
            image,
            inspectors,
            inspector_registry,
            scale_mm_per_pixel,
        )

