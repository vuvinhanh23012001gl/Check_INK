import sys
from pathlib import Path
import numpy as np
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from app.config import ClassNameObjectStructureDetectConfig
from app.judger import ArmCoverDetector, JudgmentResult


def create_detector(search_result):
    """Tạo detector với model giả trả về kết quả định trước.

    Input: ``search_result`` là output giả của ``FrameModelYoloObject.search``.
    Output: tuple gồm detector và mock model.
    Errors: không phát sinh.
    """
    model = Mock()
    model.search.return_value = search_result
    return ArmCoverDetector(model), model


def test_evaluate_with_cover_arm_present():
    """Kiểm tra evaluate trả OK khi cấu hình yêu cầu và model phát hiện Cover Arm."""
    print("\n[TEST 1] Cover Arm có trong vùng cấu hình")
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    runtime_output = (True, ["OK"], image, [{"class_name": "cover_arm"}])
    detector, model = create_detector(runtime_output)
    print("  standard_data:", True)
    print("  ROI: x1=1, y1=2, x2=10, y2=12")
    print("  runtime objects:", runtime_output[3])

    result = detector.evaluate(True, image, 1, 2, 10, 12)
    print("  judgment:", result.to_dict())

    assert isinstance(result, JudgmentResult)
    assert result.ok is True
    assert result.status == "OK"
    assert result.standard_data == {"exists": True}
    assert result.runtime_data["exists"] is True
    assert result.runtime_data["count"] == 1
    assert result.runtime_data["objects"] == runtime_output[3]
    model.search.assert_called_once_with(
        image,
        1,
        2,
        10,
        12,
        ClassNameObjectStructureDetectConfig.COVER_ARM,
    )
    print("  PASS: model.search được gọi đúng")


def test_evaluate_with_cover_arm_absent():
    """Kiểm tra evaluate trả NG khi cấu hình yêu cầu Cover Arm nhưng model không phát hiện."""
    print("\n[TEST 2] Cấu hình yêu cầu Cover Arm nhưng runtime không phát hiện")
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, _ = create_detector((False, ["Không tìm thấy"], image, []))
    print("  standard_data:", True)
    print("  runtime objects: []")

    result = detector.evaluate(True, image, 1, 2, 10, 12)
    print("  judgment:", result.to_dict())

    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["exists"] is False
    assert result.runtime_data["count"] == 0
    assert result.errors


def test_evaluate_with_empty_region():
    """Kiểm tra evaluate trả OK khi cấu hình yêu cầu vùng không có Cover Arm."""
    print("\n[TEST 3] Cấu hình yêu cầu vùng không có Cover Arm")
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, _ = create_detector((False, ["OK"], image, []))
    print("  standard_data:", False)
    print("  runtime objects: []")

    result = detector.evaluate(False, image, 1, 2, 10, 12)
    print("  judgment:", result.to_dict())

    assert result.ok is True
    assert result.status == "OK"
    assert result.standard_data == {"exists": False}
    assert result.runtime_data["objects"] == []


def test_compare_and_judge_presence():
    """Kiểm tra compare và judge độc lập với bốn trường hợp có/không có object."""
    print("\n[TEST 4] Kiểm tra compare/judge với bốn trường hợp")
    cases = [
        (True, [{"class_name": "cover_arm"}], True),
        (False, [], True),
        (True, [], False),
        (False, [{"class_name": "cover_arm"}], False),
    ]

    for standard_data, objects, expected_ok in cases:
        detector, _ = create_detector((bool(objects), [], None, objects))
        runtime_data = (bool(objects), [], None, objects)

        comparison = detector.compare(standard_data, runtime_data)
        result = detector.judge(comparison)
        print(
            f"  standard={standard_data}, runtime_count={len(objects)}, "
            f"expected={expected_ok}, actual={result.status}"
        )

        assert isinstance(result, JudgmentResult)
        assert result.ok is expected_ok
        assert result.status == ("OK" if expected_ok else "NG")
        assert result.standard_data == {"exists": standard_data}
        assert result.runtime_data["objects"] == objects
        assert result.runtime_data["count"] == len(objects)


def test_compare_rejects_invalid_standard_data():
    """Kiểm tra compare từ chối cấu hình chuẩn không phải bool."""
    print("\n[TEST 5] Từ chối standard_data không phải bool")
    detector, _ = create_detector((False, [], None, []))

    try:
        detector.compare("True", (False, [], None, []))
    except ValueError as error:
        print("  nhận ValueError:", error)
        assert "standard_data" in str(error)
    else:
        raise AssertionError("compare phải báo ValueError với standard_data sai")


def main():
    """Chạy toàn bộ test ArmCoverDetector và báo kết quả ra console."""
    tests = [
        test_evaluate_with_cover_arm_present,
        test_evaluate_with_cover_arm_absent,
        test_evaluate_with_empty_region,
        test_compare_and_judge_presence,
        test_compare_rejects_invalid_standard_data,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test: PASS")


if __name__ == "__main__":
    main()
