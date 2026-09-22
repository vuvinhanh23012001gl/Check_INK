import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import ClassNameObjectStructureDetectConfig
from app.judger import HoleDetector, JudgmentResult


def create_detector(search_result):
    """Tạo HoleDetector với kết quả search giả.

    Input: ``search_result`` là output giả của ``FrameModelYoloObject.search``.
    Output: tuple gồm detector và mock model.
    Errors: Không phát sinh.
    """
    model = Mock()
    model.search.return_value = search_result
    return HoleDetector(model), model


def test_evaluate_with_hole_present():
    """Kiểm tra evaluate trả OK khi runtime có Hole."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    objects = [{"class_name": ClassNameObjectStructureDetectConfig.HOLE.value}]
    runtime_output = (True, ["OK"], image, objects)
    detector, model = create_detector(runtime_output)

    result = detector.evaluate(True, image, 1, 2, 10, 12)

    assert isinstance(result, JudgmentResult)
    assert result.ok is True
    assert result.status == "OK"
    assert result.standard_data == {"exists": True}
    assert result.runtime_data["exists"] is True
    assert result.runtime_data["count"] == 1
    assert result.runtime_data["objects"] == objects
    model.search.assert_called_once_with(
        image,
        1,
        2,
        10,
        12,
        ClassNameObjectStructureDetectConfig.HOLE,
    )


def test_evaluate_with_hole_absent():
    """Kiểm tra evaluate trả NG khi yêu cầu Hole nhưng không phát hiện."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, _ = create_detector((False, ["Không tìm thấy"], image, []))

    result = detector.evaluate(True, image, 1, 2, 10, 12)

    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["exists"] is False
    assert result.runtime_data["count"] == 0
    assert result.errors


def test_evaluate_with_hole_not_required():
    """Kiểm tra evaluate trả OK khi vùng được cấu hình không có Hole."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, _ = create_detector((False, ["OK"], image, []))

    result = detector.evaluate(False, image, 1, 2, 10, 12)

    assert result.ok is True
    assert result.status == "OK"
    assert result.standard_data == {"exists": False}
    assert result.runtime_data["objects"] == []


def test_compare_and_judge_presence():
    """Kiểm tra bốn tổ hợp chuẩn và trạng thái Hole runtime."""
    detector, _ = create_detector((False, [], None, []))
    cases = [
        (True, [{"class_name": "hole"}], True),
        (False, [], True),
        (True, [], False),
        (False, [{"class_name": "hole"}], False),
    ]

    for standard_data, objects, expected_ok in cases:
        runtime_data = (bool(objects), [], None, objects)
        comparison = detector.compare(standard_data, runtime_data)
        result = detector.judge(comparison)

        assert isinstance(result, JudgmentResult)
        assert result.ok is expected_ok
        assert result.status == ("OK" if expected_ok else "NG")
        assert result.standard_data == {"exists": standard_data}
        assert result.runtime_data["exists"] is bool(objects)
        assert result.runtime_data["count"] == len(objects)
        assert result.runtime_data["objects"] == objects


def test_compare_rejects_invalid_input():
    """Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc."""
    detector, _ = create_detector((False, [], None, []))

    try:
        detector.compare("True", (False, [], None, []))
    except ValueError as error:
        assert "standard_data" in str(error)
    else:
        raise AssertionError("compare phải báo lỗi khi standard_data không phải bool")

    try:
        detector.compare(True, (False, [], None))
    except ValueError as error:
        assert "runtime_data" in str(error)
    else:
        raise AssertionError("compare phải báo lỗi khi runtime_data sai cấu trúc")


def main():
    """Chạy các kiểm tra logic HoleDetector và báo kết quả console.

    Input: Không có.
    Output: Không có; báo PASS hoặc ném AssertionError khi kiểm tra thất bại.
    Errors: AssertionError nếu một kiểm tra không đạt.
    """
    tests = [
        test_evaluate_with_hole_present,
        test_evaluate_with_hole_absent,
        test_evaluate_with_hole_not_required,
        test_compare_and_judge_presence,
        test_compare_rejects_invalid_input,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test logic Hole: PASS")


if __name__ == "__main__":
    main()
