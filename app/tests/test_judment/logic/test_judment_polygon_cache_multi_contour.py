import sys
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.judger import BorderDetector, Judment, JudgmentResult


class _DummyUnet:
    """Model giả cho BorderDetector trong test cache polygon.

    Input: Không có.
    Output: Instance rỗng để chia sẻ cùng `id(unet_model)` giữa inspectors.
    Errors: Không phát sinh.
    """


class _RecordingLineInspector(BorderDetector):
    """Inspector đo line giả để kiểm tra cache-hit polygon đa contour.

    Input: Nhận `unet_model`, `inspector_name` và payload runtime mẫu.
    Output: Cung cấp bộ đếm số lần gọi define/define_with_polygon và dữ liệu
        polygon/polygons thực nhận khi cache-hit.
    Errors: Không phát sinh trong test; mọi input được kiểm soát nội bộ.
    """

    INSPECTOR_NAME = "RecordingLineInspector"

    def __init__(
        self,
        unet_model: Any,
        inspector_name: str,
        runtime_payload: dict[str, Any],
    ) -> None:
        """Khởi tạo inspector giả phục vụ test.

        Input: `unet_model` dùng tạo cache key, `inspector_name` là tên key
            config runtime, và `runtime_payload` là dữ liệu define trả về.
        Output: Không trả về dữ liệu.
        Errors: Không phát sinh.
        """
        super().__init__(unet_model)
        self.INSPECTOR_NAME = inspector_name
        self._runtime_payload = runtime_payload
        self.define_calls = 0
        self.define_with_polygon_calls = 0
        self.last_cached_polygon = None
        self.last_cached_polygons = None

    def get_inspector_name(self) -> str:
        """Trả tên inspector runtime theo instance cho mục đích test.

        Input: Không có.
        Output: Tên inspector đã cấu hình khi tạo instance.
        Errors: Không phát sinh.
        """
        return self.INSPECTOR_NAME

    def define(self, image: np.ndarray, lines: list, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Giả lập define chuẩn và trả payload runtime có đa contour.

        Input: `image`, danh sách `lines` và đối số bổ sung.
        Output: Runtime payload chứa `polygon`, `polygons`, `lines`, `image`.
        Errors: Không phát sinh.
        """
        self.define_calls += 1
        return dict(self._runtime_payload)

    def define_with_polygon(
        self,
        image: np.ndarray,
        lines: list,
        polygon: Any,
        polygons: Any = None,
    ) -> dict[str, Any]:
        """Ghi lại payload polygon nhận từ cache-hit rồi trả runtime payload.

        Input: Ảnh, lines và dữ liệu polygon cache từ `Judment`.
        Output: Runtime payload chuẩn để pipeline tiếp tục.
        Errors: Không phát sinh.
        """
        self.define_with_polygon_calls += 1
        self.last_cached_polygon = polygon
        self.last_cached_polygons = polygons
        return dict(self._runtime_payload)

    def compare(
        self,
        standard_data: dict,
        runtime_data: dict,
        scale_mm_per_pixel: float,
    ) -> dict[str, Any]:
        """So sánh giả lập, chỉ chuyển tiếp metadata polygon cho overlay/debug.

        Input: Dữ liệu chuẩn inspector, runtime_data và scale calibration.
        Output: Dict comparison tối thiểu có `comparisons`, `polygon`,
            `polygons`, `image`.
        Errors: Không phát sinh.
        """
        _ = (standard_data, scale_mm_per_pixel)
        return {
            "comparisons": [],
            "polygon": runtime_data.get("polygon"),
            "polygons": runtime_data.get("polygons"),
            "image": runtime_data.get("image"),
        }

    def judge(self, comparison_data: dict) -> JudgmentResult:
        """Phán định giả lập luôn OK cho test luồng cache.

        Input: `comparison_data` output từ `compare`.
        Output: `JudgmentResult` trạng thái OK.
        Errors: Không phát sinh.
        """
        return JudgmentResult(
            ok=True,
            status="OK",
            standard_data={},
            runtime_data=comparison_data,
            comparison_data=comparison_data,
            message="cache polygon test",
            errors=[],
        )


def _build_runtime_payload() -> dict[str, Any]:
    """Tạo runtime payload có primary polygon và danh sách 2 contour.

    Input: Không có.
    Output: Dict runtime mô phỏng output của BorderDetector.define.
    Errors: Không phát sinh.
    """
    polygon_primary = [[20, 20], [220, 20], [220, 120], [20, 120]]
    polygon_secondary = [[260, 140], [360, 140], [360, 280], [260, 280]]
    return {
        "polygon": polygon_primary,
        "polygons": [polygon_primary, polygon_secondary],
        "lines": [
            {
                "line_index": 0,
                "original_line": [230.0, 180.0, 360.0, 180.0],
                "intersection_point_1": [260.0, 180.0],
                "intersection_point_2": [360.0, 180.0],
                "intersection_count": 2,
                "distance_pixel": 100.0,
                "is_valid": True,
            }
        ],
        "image": np.zeros((400, 400, 3), dtype=np.uint8),
    }


def main() -> None:
    """Kiểm tra inspector thứ hai nhận đủ đa contour khi cache-hit.

    Input: Không có; dùng dữ liệu giả lập trong test này.
    Output: In PASS nếu cache-hit truyền đủ `polygons` cho define_with_polygon.
    Errors: AssertionError nếu `Judment` chỉ truyền primary polygon.
    """
    shared_unet = _DummyUnet()
    payload = _build_runtime_payload()
    inspector_a = _RecordingLineInspector(
        shared_unet,
        "MeasurementWeldInspector",
        payload,
    )
    inspector_b = _RecordingLineInspector(
        shared_unet,
        "BorderFilmInspector",
        payload,
    )

    registry = {
        "MeasurementWeldInspector": inspector_a,
        "BorderFilmInspector": inspector_b,
    }
    config = {
        "MeasurementWeldInspector": {
            "0": {
                "name_line": "1",
                "level1": 0.1,
                "level2": 0.2,
                "level3": 0.3,
                "level4": 0.4,
                "level5": 0.5,
                "xStart": 1532,
                "yStart": 424,
                "xEnd": 1440,
                "yEnd": 638,
                "coordinateSpace": "image",
            }
        },
        "BorderFilmInspector": {
            "0": {
                "nameLine": "1",
                "widthMin": 2,
                "widthMax": 3,
                "xStart": 1250,
                "yStart": 194,
                "xEnd": 1188,
                "yEnd": 394,
                "coordinateSpace": "image",
            }
        },
    }

    image = np.zeros((400, 400, 3), dtype=np.uint8)
    summary = Judment(registry).run_summary(image, config, scale_mm_per_pixel=0.02)

    assert summary["status"] == "OK"
    assert inspector_a.define_calls == 1
    assert inspector_a.define_with_polygon_calls == 0
    assert inspector_b.define_calls == 0
    assert inspector_b.define_with_polygon_calls == 1
    assert isinstance(inspector_b.last_cached_polygons, list)
    assert len(inspector_b.last_cached_polygons) == 2

    print("Judment polygon cache multi-contour test: PASS")


if __name__ == "__main__":
    main()
