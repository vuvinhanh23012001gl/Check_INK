import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import ClassNameModelSurfaceConfig
from app.judger import JudgmentResult, ScratchThePipeDetector


def create_detector(runtime_result):
    """Tạo ScratchThePipeDetector với model phủ định giả.

    Input: ``runtime_result`` là output giả của ``search_negative``.
    Output: tuple gồm detector và mock model.
    Errors: Không phát sinh.
    """
    model = Mock()
    model.search_negative.return_value = runtime_result
    return ScratchThePipeDetector(model), model


def test_scratch_found_is_ng():
    """Khi phát hiện Scratch, vùng không sạch và kết quả phải là NG."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, model = create_detector((False, ["Phát hiện scratch"], image))

    result = detector.evaluate(True, image, 1, 2, 10, 12)

    assert isinstance(result, JudgmentResult)
    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["scratch_found"] is True
    assert result.errors
    model.search_negative.assert_called_once_with(
        image,
        1,
        2,
        10,
        12,
        ClassNameModelSurfaceConfig.SCRATCH,
    )


def test_no_scratch_is_ok():
    """Khi không phát hiện Scratch, vùng sạch và kết quả phải là OK."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, _ = create_detector((True, ["Không phát hiện scratch"], image))

    result = detector.evaluate(True, image, 1, 2, 10, 12)

    assert result.ok is True
    assert result.status == "OK"
    assert result.runtime_data["scratch_found"] is False
    assert result.errors == []


def test_compare_rejects_invalid_input():
    """Kiểm tra compare từ chối chuẩn và runtime sai cấu trúc."""
    detector, _ = create_detector((True, [], None))

    try:
        detector.compare(False, (True, [], None))
    except ValueError as error:
        assert "True" in str(error)
    else:
        raise AssertionError("compare phải từ chối standard_data=False")

    try:
        detector.compare(True, (True, []))
    except ValueError as error:
        assert "runtime_data" in str(error)
    else:
        raise AssertionError("compare phải từ chối runtime_data sai cấu trúc")


def test_judge_requires_comparison_data():
    """Kiểm tra judge báo lỗi khi thiếu dữ liệu so sánh bắt buộc."""
    detector, _ = create_detector((True, [], None))

    try:
        detector.judge({"runtime_clean": True})
    except ValueError as error:
        assert "comparison_data" in str(error)
    else:
        raise AssertionError("judge phải báo lỗi khi thiếu comparison_data")


def main():
    """Chạy test logic ScratchThePipeDetector và báo kết quả console.

    Input: Không có.
    Output: Không có; in PASS nếu toàn bộ kiểm tra thành công.
    Errors: AssertionError hoặc ValueError nếu logic không đúng mong đợi.
    """
    tests = [
        test_scratch_found_is_ng,
        test_no_scratch_is_ok,
        test_compare_rejects_invalid_input,
        test_judge_requires_comparison_data,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test logic Scratch: PASS")


if __name__ == "__main__":
    main()
