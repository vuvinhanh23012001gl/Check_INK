import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from app.judger import Judment, MeasurementWeldingDetector


STANDARD_LINE = {
    "name_line": "1",
    "level1": 2,
    "level2": 3,
    "level3": 4,
    "level4": 5,
    "level5": 6,
    "xStart": 0,
    "yStart": 5,
    "xEnd": 10,
    "yEnd": 5,
}


def create_detector() -> tuple[MeasurementWeldingDetector, Mock]:
    """Tạo detector với polygon chữ nhật giả để test logic không cần model thật.

    Input: Không có.
    Output: Detector và mock UNet trả polygon từ x=3 đến x=7.
    Errors: Không phát sinh.
    """
    model = Mock()
    model.get_polygon.return_value = np.array(
        [[[3, 2]], [[7, 2]], [[7, 8]], [[3, 8]]],
        dtype=np.int32,
    )
    return MeasurementWeldingDetector(model), model


def create_runtime(distance_mm: float, is_valid: bool = True) -> dict:
    """Tạo output define giả với khoảng cách pixel bằng khoảng cách mm.

    Input: Khoảng cách cần kiểm tra và trạng thái line runtime.
    Output: Dictionary runtime tương thích MeasurementWeldingDetector.compare.
    Errors: Không phát sinh.
    """
    return {
        "polygon": None,
        "lines": [{
            "line_index": 0,
            "original_line": (0, 5, 10, 5),
            "intersection_point_1": (3, 5),
            "intersection_point_2": (7, 5),
			"intersection_count": 2 if is_valid else 0,
            "distance_pixel": distance_mm,
            "is_valid": is_valid,
        }],
    }


def test_levels() -> None:
    """Kiểm tra level 1, 2, 3, 5 là NG và level 4 là OK.

    Input: Dữ liệu chuẩn level1=2, level2=3, level3=4, level4=5, level5=6.
    Output: Không trả về; assert trạng thái và level từng trường hợp.
    Errors: AssertionError nếu luật level không đúng.
    """
    detector, _ = create_detector()
    cases = [
        (1.5, 1, False),
        (2.5, 2, False),
        (3.5, 3, False),
        (4.5, 4, True),
        (5.5, 5, False),
    ]
    standard = {"MeasurementWeldInspector": {"0": STANDARD_LINE}}
    for distance_mm, expected_level, expected_ok in cases:
        comparison = detector.compare(
            standard,
            create_runtime(distance_mm),
            scale_mm_per_pixel=1.0,
        )
        line = comparison["comparisons"][0]
        result = detector.judge(comparison)
        print(
            f"distance={distance_mm} mm -> level={line['level']}, "
            f"status={result.status}"
        )
        assert line["level"] == expected_level
        assert result.ok is expected_ok


def test_finite_line_intersection_count() -> None:
    """Kiểm tra Measurement không kéo dài line ngoài tọa độ cấu hình.

    Input: Ba đoạn line có lần lượt 0, 1 và 2 giao điểm với polygon.
    Output: Chỉ đoạn có đúng 2 giao điểm mới hợp lệ và có khoảng cách.
    Errors: AssertionError nếu line bị kéo dài hoặc đếm giao điểm sai.
    """
    detector, _ = create_detector()
    image = np.zeros((10, 11, 3), dtype=np.uint8)

    runtime = detector.define(
        image,
        [
            (0, 0, 2, 0),
            (0, 5, 3, 5),
            (0, 5, 10, 5),
        ],
    )

    no_intersection, one_intersection, two_intersections = runtime["lines"]
    print("0 điểm:", no_intersection)
    print("1 điểm:", one_intersection)
    print("2 điểm:", two_intersections)
    assert no_intersection["intersection_count"] == 0
    assert no_intersection["is_valid"] is False
    assert one_intersection["intersection_count"] == 1
    assert one_intersection["intersection_point_1"] == (3.0, 5.0)
    assert one_intersection["is_valid"] is False
    assert two_intersections["intersection_count"] == 2
    assert two_intersections["distance_pixel"] == 4.0
    assert two_intersections["is_valid"] is True


def test_json_coordinates_are_used_to_measure() -> None:
    """Kiểm tra tọa độ chuẩn được dùng làm line đo trên polygon runtime.

    Input: Cấu hình MeasurementWeldInspector chứa tọa độ và năm level.
    Output: Kết quả OK level 4 với khoảng cách giao polygon bằng 4 pixel/mm.
    Errors: AssertionError nếu tọa độ không được truyền đúng hoặc phán định sai.
    """
    detector, model = create_detector()
    image = np.zeros((10, 11, 3), dtype=np.uint8)
    config = {"MeasurementWeldInspector": {"0": STANDARD_LINE}}

    result = Judment({
        "MeasurementWeldInspector": detector,
    }).run(image, config, scale_mm_per_pixel=1.0)["MeasurementWeldInspector"]

    comparison = result.comparison_data["comparisons"][0]
    print("standard_line:", comparison["standard_line"])
    print("runtime_line:", comparison["runtime"])
    print("distance_mm:", comparison["distance_mm"])
    print("level:", comparison["level"])
    print("status:", result.status)
    assert model.get_polygon.call_count == 1
    assert comparison["runtime"]["original_line"] == (0.0, 5.0, 10.0, 5.0)
    assert comparison["distance_mm"] == 4.0
    assert comparison["level"] == 4
    assert result.ok is True


def test_invalid_runtime_line_is_ng() -> None:
    """Kiểm tra line không cắt polygon luôn cho kết quả NG.

    Input: Runtime line có ``is_valid=False``.
    Output: Kết quả NG và level=None.
    Errors: AssertionError nếu line lỗi vẫn được xem là OK.
    """
    detector, _ = create_detector()
    standard = {"0": STANDARD_LINE}
    comparison = detector.compare(
        standard,
        create_runtime(0.0, is_valid=False),
        scale_mm_per_pixel=1.0,
    )
    result = detector.judge(comparison)
    assert comparison["comparisons"][0]["level"] is None
    assert result.ok is False
    assert result.errors


def main() -> None:
    """Chạy toàn bộ test logic MeasurementWeldingDetector bằng Python thường."""
    tests = [
        test_levels,
        test_finite_line_intersection_count,
        test_json_coordinates_are_used_to_measure,
        test_invalid_runtime_line_is_ng,
    ]
    for test in tests:
        print(f"\n===== {test.__name__} =====")
        test()
        print("PASS")
    print(f"\nĐã chạy {len(tests)} test MeasurementWeldingDetector: PASS")


if __name__ == "__main__":
    main()
