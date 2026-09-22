import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from app.judger import Judment, SlitDetector


STANDARD_LINE = {
    "nameLine": "1",
    "widthMin": 2,
    "widthMax": 3,
    "xStart": 0,
    "yStart": 5,
    "xEnd": 10,
    "yEnd": 5,
}


def create_detector() -> tuple[SlitDetector, Mock]:
    """Tạo SlitDetector với polygon chữ nhật giả.

    Input: Không có.
    Output: Detector và mock UNet trả polygon từ x=3 đến x=7.
    Errors: Không phát sinh.
    """
    model = Mock()
    model.get_polygon.return_value = np.array(
        [[[3, 2]], [[7, 2]], [[7, 8]], [[3, 8]]],
        dtype=np.int32,
    )
    return SlitDetector(model), model


def create_runtime(distance_mm: float, is_valid: bool = True) -> dict:
    """Tạo output runtime giả với scale 1 pixel bằng 1 mm.

    Input: khoảng cách và trạng thái giao polygon.
    Output: dict output tương thích với ``define``.
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


def test_width_range_boundaries() -> None:
    """Kiểm tra trong khoảng và hai biên min/max là OK, ngoài khoảng là NG."""
    detector, _ = create_detector()
    standard = {"SlitWeldInspector": {"0": STANDARD_LINE}}
    cases = [
        (1.99, False),
        (2.0, True),
        (2.5, True),
        (3.0, True),
        (3.01, False),
    ]
    for distance_mm, expected_ok in cases:
        comparison = detector.compare(
            standard,
            create_runtime(distance_mm),
            scale_mm_per_pixel=1.0,
        )
        result = detector.judge(comparison)
        print(
            f"distance={distance_mm} mm, chuẩn=2..3 mm, "
            f"status={result.status}"
        )
        assert result.ok is expected_ok


def test_finite_line_intersection_count() -> None:
    """Kiểm tra chỉ giao điểm nằm trên đoạn line cấu hình được sử dụng.

    Input: Ba đoạn line lần lượt không chạm, chạm một điểm và cắt hai điểm.
    Output: Số giao điểm tương ứng 0, 1, 2; chỉ hai điểm là hợp lệ.
    Errors: AssertionError nếu detector kéo dài line hoặc tính sai giao điểm.
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


def test_json_coordinates_are_used_by_judgment() -> None:
    """Kiểm tra Judment dùng đúng tọa độ SlitWeldInspector để đo polygon."""
    detector, model = create_detector()
    image = np.zeros((10, 11, 3), dtype=np.uint8)
    config = {"SlitWeldInspector": {
        "0": {**STANDARD_LINE, "widthMin": 3.5, "widthMax": 4.5}
    }}

    result = Judment({"SlitWeldInspector": detector}).run(
        image,
        config,
        scale_mm_per_pixel=1.0,
    )["SlitWeldInspector"]

    item = result.comparison_data["comparisons"][0]
    print("standard_line:", item["standard_line"])
    print("runtime_line:", item["runtime"])
    print("distance_mm:", item["distance_mm"])
    print("status:", result.status)
    assert model.get_polygon.call_count == 1
    assert item["runtime"]["original_line"] == (0.0, 5.0, 10.0, 5.0)
    assert item["distance_mm"] == 4.0
    assert result.ok is True


def test_invalid_runtime_line_is_ng() -> None:
    """Kiểm tra line không cắt polygon luôn là NG."""
    detector, _ = create_detector()
    comparison = detector.compare(
        {"0": STANDARD_LINE},
        create_runtime(2.5, is_valid=False),
        scale_mm_per_pixel=1.0,
    )
    result = detector.judge(comparison)
    assert result.ok is False
    assert result.errors


def test_invalid_width_range_is_rejected() -> None:
    """Kiểm tra widthMin lớn hơn hoặc bằng widthMax bị từ chối."""
    detector, _ = create_detector()
    invalid_standard = {"0": {**STANDARD_LINE, "widthMin": 3, "widthMax": 3}}
    try:
        detector.compare(
            invalid_standard,
            create_runtime(3.0),
            scale_mm_per_pixel=1.0,
        )
    except ValueError as error:
        assert "widthMin" in str(error)
    else:
        raise AssertionError("SlitDetector phải từ chối khoảng width không hợp lệ")


def main() -> None:
    """Chạy toàn bộ test logic SlitDetector bằng Python thường."""
    tests = [
        test_width_range_boundaries,
        test_finite_line_intersection_count,
        test_json_coordinates_are_used_by_judgment,
        test_invalid_runtime_line_is_ng,
        test_invalid_width_range_is_rejected,
    ]
    for test in tests:
        print(f"\n===== {test.__name__} =====")
        test()
        print("PASS")
    print(f"\nĐã chạy {len(tests)} test SlitDetector: PASS")


if __name__ == "__main__":
    main()
