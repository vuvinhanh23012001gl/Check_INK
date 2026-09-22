import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.judger import BorderDetector, JudgmentResult


def create_detector():
    """Tạo BorderDetector với polygon hình chữ nhật giả."""
    model = Mock()
    model.get_polygon.return_value = np.array(
        [[[10, 10]], [[90, 10]], [[90, 90]], [[10, 90]]],
        dtype=np.int32,
    )
    return BorderDetector(model), model


def test_define_uses_one_unet_call_and_exact_points():
    """Một ảnh có nhiều line chỉ gọi UNet một lần và lấy giao điểm chính xác."""
    detector, model = create_detector()
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    runtime = detector.define(image, [(0, 50, 99, 50), (50, 0, 50, 99)])

    assert model.get_polygon.call_count == 1
    assert runtime["lines"][0]["intersection_point_1"] == (10.0, 50.0)
    assert runtime["lines"][0]["intersection_point_2"] == (90.0, 50.0)
    assert runtime["lines"][0]["distance_pixel"] == 80.0
    assert runtime["lines"][1]["intersection_point_1"] == (50.0, 10.0)
    assert runtime["lines"][1]["intersection_point_2"] == (50.0, 90.0)
    assert runtime["lines"][1]["distance_pixel"] == 80.0


def test_compare_and_judge_border_widths():
    """Line có khoảng cách trong min/max phải cho kết quả OK."""
    detector, _ = create_detector()
    runtime = {
        "polygon": None,
        "lines": [
            {
                "line_index": 0,
                "distance_pixel": 80.0,
                "is_valid": True,
            },
            {
                "line_index": 1,
                "distance_pixel": 80.0,
                "is_valid": True,
            },
        ],
    }
    standard = {
        "BorderFilmInspector": {
            "0": {"widthMin": 7, "widthMax": 9},
            "1": {"widthMin": 8, "widthMax": 8},
        }
    }

    comparison = detector.compare(standard, runtime, scale_mm_per_pixel=0.1)
    result = detector.judge(comparison)

    assert isinstance(result, JudgmentResult)
    assert result.ok is True
    assert result.status == "OK"
    assert all(item["is_valid"] for item in comparison["comparisons"])
    assert comparison["comparisons"][0]["distance_mm"] == 8.0


def test_compare_and_judge_out_of_range_is_ng():
    """Line đo vượt widthMax phải cho kết quả NG."""
    detector, _ = create_detector()
    runtime = {
        "polygon": None,
        "lines": [
            {"line_index": 0, "distance_pixel": 80.0, "is_valid": True},
        ],
    }
    standard = {"0": {"widthMin": 2, "widthMax": 3}}

    result = detector.judge(detector.compare(standard, runtime, scale_mm_per_pixel=0.1))

    assert result.ok is False
    assert result.status == "NG"
    assert result.errors


def test_line_without_intersection_is_ng():
    """Line không cắt polygon phải là NG dù có chuẩn width."""
    detector, _ = create_detector()
    runtime = {
        "polygon": None,
        "lines": [
            {"line_index": 0, "distance_pixel": 0.0, "is_valid": False},
        ],
    }
    standard = {"0": {"widthMin": 2, "widthMax": 3}}

    result = detector.judge(detector.compare(standard, runtime, scale_mm_per_pixel=0.1))

    assert result.ok is False
    assert result.status == "NG"


def test_invalid_input_is_rejected():
    """Dữ liệu chuẩn thiếu widthMin/widthMax phải báo ValueError."""
    detector, _ = create_detector()
    runtime = {"polygon": None, "lines": []}

    try:
        detector.compare({"0": {"widthMin": 2}}, runtime, scale_mm_per_pixel=0.1)
    except ValueError as error:
        assert "widthMin/widthMax" in str(error)
    else:
        raise AssertionError("compare phải từ chối chuẩn thiếu widthMax")


def main():
    """Chạy test logic BorderDetector và báo kết quả console.

    Input: Không có.
    Output: Không có; in PASS nếu toàn bộ kiểm tra thành công.
    Errors: AssertionError hoặc ValueError nếu logic không đúng mong đợi.
    """
    tests = [
        test_define_uses_one_unet_call_and_exact_points,
        test_compare_and_judge_border_widths,
        test_compare_and_judge_out_of_range_is_ng,
        test_line_without_intersection_is_ng,
        test_invalid_input_is_rejected,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test logic BorderDetector: PASS")


if __name__ == "__main__":
    main()
