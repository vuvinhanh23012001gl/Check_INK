from dataclasses import dataclass, field
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Sequence
import numpy as np
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
        }

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

