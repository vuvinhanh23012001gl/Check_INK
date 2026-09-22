import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import ClassNameModelSurfaceConfig
from app.judger import JudgmentResult, WeldSeamAirBubbles


def create_detector(runtime_result):
    """Tạo detector với model bọt khí giả.

    Input: ``runtime_result`` là output giả của ``search_negative``.
    Output: detector và mock model.
    Errors: Không phát sinh.
    """
    model = Mock()
    model.search_negative.return_value = runtime_result
    return WeldSeamAirBubbles(model), model


def test_bubble_found_is_ng():
    """Khi có bọt khí trong vùng đường hàn, kết quả phải là NG."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, model = create_detector((False, ["Phát hiện bọt khí"], image))

    result = detector.evaluate(True, image, [(1, 2, 8, 9)])

    assert isinstance(result, JudgmentResult)
    assert result.ok is False
    assert result.status == "NG"
    assert result.runtime_data["air_bubble_found"] is True
    assert model.search_negative.call_count == 1
    call_args = model.search_negative.call_args.args
    assert np.array_equal(call_args[0], image)
    assert call_args[1:] == (
        1,
        2,
        9,
        11,
        ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
    )


def test_no_bubble_is_ok():
    """Khi không có bọt khí trong vùng đường hàn, kết quả phải là OK."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, model = create_detector((True, ["Vùng sạch"], image))

    result = detector.evaluate(True, image, [(1, 2, 8, 9)])

    assert result.ok is True
    assert result.status == "OK"
    assert result.runtime_data["air_bubble_found"] is False
    model.search_negative.assert_called_once()


def test_no_abnormal_regions_is_ok_without_inference():
    """Không có vùng giao đường hàn thì trả OK và không gọi model."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, model = create_detector((False, [], image))

    result = detector.evaluate(True, image, [])

    assert result.ok is True
    assert result.status == "OK"
    model.search_negative.assert_not_called()


def test_other_class_does_not_change_bubble_rule():
    """Detector chỉ gọi class air_bubble, không kiểm tra mọi class khác."""
    image = np.zeros((20, 30, 3), dtype=np.uint8)
    detector, model = create_detector((True, ["Không có air_bubble"], image))

    result = detector.evaluate(True, image, [(0, 0, 5, 5)])

    assert result.ok is True
    assert result.status == "OK"
    assert model.search_negative.call_args.args[-1] == "air_bubble"


def test_four_configured_regions_with_one_bubble_are_ng():
    """Một bọt khí trong bất kỳ một trong bốn vùng đều làm tổng thể NG.

    Input: Bốn vùng dạng dict giống cấu hình AirBubblesItemInspector.
    Output: Kết quả tổng là NG và model được gọi một lần cho mỗi vùng.
    Errors: AssertionError nếu detector bỏ qua vùng hoặc phân định sai.
    """
    image = np.zeros((500, 1000, 3), dtype=np.uint8)
    model = Mock()
    model.search_negative.side_effect = [
        (True, ["Vùng 1 sạch"], image),
        (True, ["Vùng 2 sạch"], image),
        (True, ["Vùng 3 sạch"], image),
        (False, ["Phát hiện bọt khí vùng 4"], image),
    ]
    detector = WeldSeamAirBubbles(model)
    regions = [
        {"id": 0, "xStart": 827, "yStart": 178, "xEnd": 947, "yEnd": 296},
        {"id": 1, "xStart": 558, "yStart": 42, "xEnd": 681, "yEnd": 104},
        {"id": 2, "xStart": 179, "yStart": 98, "xEnd": 476, "yEnd": 261},
        {"id": 3, "xStart": 299, "yStart": 318, "xEnd": 467, "yEnd": 394},
    ]

    result = detector.evaluate(True, image, regions)

    assert result.ok is False
    assert result.status == "NG"
    assert model.search_negative.call_count == 4


def test_compare_rejects_invalid_input():
    """Kiểm tra compare từ chối chuẩn hoặc runtime sai cấu trúc."""
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


def main():
    """Chạy test logic WeldSeamAirBubbles và báo kết quả console.

    Input: Không có.
    Output: Không có; in PASS nếu toàn bộ kiểm tra thành công.
    Errors: AssertionError hoặc ValueError nếu logic không đúng mong đợi.
    """
    tests = [
        test_bubble_found_is_ng,
        test_no_bubble_is_ok,
        test_no_abnormal_regions_is_ok_without_inference,
        test_other_class_does_not_change_bubble_rule,
        test_four_configured_regions_with_one_bubble_are_ng,
        test_compare_rejects_invalid_input,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"Đã chạy {len(tests)} test logic bọt khí: PASS")


if __name__ == "__main__":
    main()
