import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.judger import JudgmentResult, SemiPermeableMembrane


def create_detector(border_segments, inner_segments):
    """Tạo detector với kết quả segmentation giả.

    Input: ``border_segments`` và ``inner_segments`` là danh sách segment giả.
    Output: detector và hai mock frame model.
    Errors: Không phát sinh.
    """
    border_model = Mock()
    inner_model = Mock()
    border_model.get_segments.return_value = border_segments
    inner_model.get_segments.return_value = inner_segments
    detector = SemiPermeableMembrane(border_model, inner_model)
    return detector, border_model, inner_model


def segment(polygon, class_id=0):
    """Tạo một segment polygon tối thiểu cho test."""
    return {
        "class_id": class_id,
        "class_name": "membrane",
        "confidence": 0.99,
        "polygon": polygon,
    }


def test_inner_completely_inside_is_ok():
    """Inner nằm hoàn toàn trong border phải trả về OK."""
    border = [(0, 0), (10, 0), (10, 10), (0, 10)]
    inner = [(2, 2), (8, 2), (8, 8), (2, 8)]
    detector, border_model, inner_model = create_detector(
        [segment(border)],
        [segment(inner)],
    )
    image = np.zeros((20, 20, 3), dtype=np.uint8)

    result = detector.evaluate(True, image, 1, 2, 19, 19)

    assert isinstance(result, JudgmentResult)
    assert result.ok is True
    assert result.status == "OK"
    assert result.runtime_data["inner_completely_inside_border"] is True
    assert result.runtime_data["intersection_points"] is None
    border_model.get_segments.assert_called_once_with(image, 1, 2, 19, 19)
    inner_model.get_segments.assert_called_once_with(image, 1, 2, 19, 19)


def test_inner_overlapping_border_is_ng():
    """Inner đè lên border phải trả về NG."""
    border = [(0, 0), (10, 0), (10, 10), (0, 10)]
    inner = [(5, 5), (15, 5), (15, 15), (5, 15)]
    detector, _, _ = create_detector([segment(border)], [segment(inner)])
    image = np.zeros((20, 20, 3), dtype=np.uint8)

    result = detector.evaluate(True, image, 0, 0, 20, 20)

    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["inner_completely_inside_border"] is False
    assert result.errors
    assert result.runtime_data["intersection_points"]


def test_inner_outside_border_is_ng():
    """Inner nằm ngoài border cũng phải trả về NG."""
    border = [(0, 0), (10, 0), (10, 10), (0, 10)]
    inner = [(20, 20), (30, 20), (30, 30), (20, 30)]
    detector, _, _ = create_detector([segment(border)], [segment(inner)])
    image = np.zeros((40, 40, 3), dtype=np.uint8)

    result = detector.evaluate(True, image, 0, 0, 40, 40)

    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["inner_completely_inside_border"] is False
    assert result.runtime_data["intersection_points"] == []


def test_missing_polygon_is_ng():
    """Thiếu border hoặc inner phải trả về NG, không được coi là đạt."""
    detector, _, _ = create_detector([], [segment([(2, 2), (8, 2), (8, 8), (2, 8)])])
    image = np.zeros((20, 20, 3), dtype=np.uint8)

    result = detector.evaluate(True, image, 0, 0, 20, 20)

    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["intersection_points"] is None


def test_compare_rejects_false_standard():
    """Luật cố định phải từ chối standard_data khác True."""
    detector, _, _ = create_detector([], [])

    try:
        detector.compare(False, (True, None, None))
    except ValueError as error:
        assert "True" in str(error)
    else:
        raise AssertionError("compare phải từ chối standard_data=False")


def main():
    """Chạy test logic SemiPermeableMembrane và báo kết quả console.

    Input: Không có.
    Output: Không có; in PASS nếu toàn bộ kiểm tra thành công.
    Errors: AssertionError hoặc ValueError nếu logic không đúng mong đợi.
    """
    tests = [
        test_inner_completely_inside_is_ok,
        test_inner_overlapping_border_is_ng,
        test_inner_outside_border_is_ng,
        test_missing_polygon_is_ng,
        test_compare_rejects_false_standard,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test logic màng bán thấm: PASS")


if __name__ == "__main__":
    main()
