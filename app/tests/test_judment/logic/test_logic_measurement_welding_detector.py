import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from app.judger import Judment, MeasurementWeldingDetector, SlitDetector


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
    """Kiểm tra level 1-3 là NG, level 4-5 là OK và ngoài level5 là NG.

    Input: Các ngưỡng trên level1=2, level2=3, level3=4, level4=5, level5=6.
    Output: Không trả về; assert trạng thái và level từng trường hợp.
    Errors: AssertionError nếu luật level không đúng.
    """
    detector, _ = create_detector()
    cases = [
        (0.0, 1, False),
        (2.0, 1, False),
        (2.5, 2, False),
        (3.0, 2, False),
        (3.5, 3, False),
        (4.0, 3, False),
        (4.5, 4, True),
        (5.0, 4, True),
        (5.5, 5, True),
        (6.0, 5, True),
        (6.1, None, False),
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
        if not expected_ok:
            assert result.errors[0].startswith(
                '[Khoảng cách đường hàn] NG - "1" - Quy định:"5 mm - 6 mm"'
            )
            assert result.errors[0].endswith(
                f'Thực tế :"{distance_mm:g} mm"'
            )


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

    Input: Cấu hình MeasurementWeldInspector với level3=3.5 và level4=5.
    Output: Kết quả OK level 4 với khoảng cách giao polygon bằng 4 pixel/mm.
    Errors: AssertionError nếu tọa độ không được truyền đúng hoặc phán định sai.
    """
    detector, model = create_detector()
    image = np.zeros((10, 11, 3), dtype=np.uint8)
    measurement_line = {**STANDARD_LINE, "level3": 3.5}
    config = {"MeasurementWeldInspector": {"0": measurement_line}}

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


def test_measurement_and_slit_share_polygon_per_run() -> None:
    """Chỉ chạy UNet một lần khi hai detector cùng model đo cùng ảnh.

    Input: Cấu hình MeasurementWeldInspector và SlitWeldInspector trên một ảnh.
    Output: Không trả về; assert số lần infer, polygon và line overlay.
    Errors: AssertionError nếu model bị gọi lặp hoặc overlay thiếu dữ liệu.
    """
    model = Mock()
    model.get_polygon.return_value = np.array(
        [[[3, 2]], [[7, 2]], [[7, 8]], [[3, 8]]],
        dtype=np.int32,
    )
    measurement = MeasurementWeldingDetector(model)
    slit = SlitDetector(model)
    image = np.zeros((10, 11, 3), dtype=np.uint8)
    line = {key: value for key, value in STANDARD_LINE.items() if key != "name_line"}
    configuration = {
        "MeasurementWeldInspector": {
            "0": {**line, "name_line": "Width", "level3": 4, "level4": 5},
        },
        "SlitWeldInspector": {
            "0": {
                **line,
                "nameLine": "Slit",
                "widthMin": 0,
                "widthMax": 10,
            },
        },
    }
    judment = Judment({
        "MeasurementWeldInspector": measurement,
        "SlitWeldInspector": slit,
    })

    first_result = judment.run_summary(image, configuration, scale_mm_per_pixel=1.0)

    assert model.get_polygon.call_count == 1
    for inspector_name in configuration:
        assert first_result["overlay_data"][inspector_name]["runtime"]["polygons"]
        assert first_result["overlay_data"][inspector_name]["standard"]["lines"] == [
            [0, 5, 10, 5]
        ]
    assert np.any(first_result["judgment_image"][2, 3])

    judment.run_summary(image, configuration, scale_mm_per_pixel=1.0)
    assert model.get_polygon.call_count == 2


def test_retrain_inputs_are_saved_per_inspector() -> None:
    """Lưu crop từng ROI và full-frame thực nhận của inspector đo line.

    Input: Ảnh giả lập cùng ROI đơn, ROI bọt khí và line UNet.
    Output: Không trả về; assert folder inspector và kích thước ảnh đã lưu.
    Errors: AssertionError nếu crop/file lưu sai hoặc dùng nhầm full-frame.
    """
    image = np.zeros((40, 60, 3), dtype=np.uint8)
    original_root = Judment.RETRAIN_OUTPUT_DIR
    with TemporaryDirectory() as temp_dir:
        Judment.RETRAIN_OUTPUT_DIR = Path(temp_dir)
        try:
            single_roi_paths = Judment._save_training_inputs(
                image,
                "ArmCoverInspector",
                (5, 7, 25, 27),
            )
            assert len(single_roi_paths) == 1
            relative_path = single_roi_paths[0].relative_to(Path(temp_dir))
            assert relative_path.parts[0] == "ArmCoverInspector"
            assert len(relative_path.parts) == 3
            assert relative_path.parts[1].count("_") == 2
            assert "session" not in str(relative_path)
            assert "product" not in str(relative_path)
            assert cv2.imread(str(single_roi_paths[0])).shape[:2] == (20, 20)

            bubble_paths = Judment._save_training_inputs(
                image,
                "AirBubblesItemInspector",
                ([(2, 3, 10, 8), (20, 10, 15, 12)],),
            )
            assert len(bubble_paths) == 2
            assert [cv2.imread(str(path)).shape[:2] for path in bubble_paths] == [
                (8, 10),
                (12, 15),
            ]

            line_paths = Judment._save_training_inputs(
                image,
                "MeasurementWeldInspector",
                ([(5, 0, 5, 39)],),
            )
            assert cv2.imread(str(line_paths[0])).shape[:2] == (40, 60)
        finally:
            Judment.RETRAIN_OUTPUT_DIR = original_root


def test_run_summary_saves_input_before_model_call() -> None:
    """Xác nhận ảnh train được ghi trước khi model UNet nhận ảnh.

    Input: Một item measurement, ảnh giả lập và context runtime.
    Output: Không trả về; assert file tồn tại ngay tại thời điểm inference.
    Errors: AssertionError nếu ảnh chưa lưu hoặc sai folder inspector.
    """
    detector, model = create_detector()
    image = np.zeros((10, 11, 3), dtype=np.uint8)
    original_root = Judment.RETRAIN_OUTPUT_DIR

    with TemporaryDirectory() as temp_dir:
        Judment.RETRAIN_OUTPUT_DIR = Path(temp_dir)

        def verify_saved_before_inference(*args, **kwargs):
            saved_files = list(Path(temp_dir).rglob("*.jpg"))
            assert len(saved_files) == 1
            assert "MeasurementWeldInspector" in saved_files[0].parts
            assert cv2.imread(str(saved_files[0])).shape[:2] == image.shape[:2]
            return np.array([[[3, 2]], [[7, 2]], [[7, 8]], [[3, 8]]], dtype=np.int32)

        model.get_polygon.side_effect = verify_saved_before_inference
        try:
            Judment({"MeasurementWeldInspector": detector}).run_summary(
                image,
                {"MeasurementWeldInspector": {"0": STANDARD_LINE}},
                scale_mm_per_pixel=1.0,
                training_context={
                    "session_id": "test-session",
                    "product_id": 1,
                    "frame_id": 0,
                    "item_id": 0,
                },
            )
            assert model.get_polygon.call_count == 1
        finally:
            Judment.RETRAIN_OUTPUT_DIR = original_root


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
    assert result.errors == [
        '[Khoảng cách đường hàn] NG - "1" - '
        'Quy định:"5 mm - 6 mm" - Thực tế :"Không đo được (0 giao điểm)"'
    ]


def main() -> None:
    """Chạy toàn bộ test logic MeasurementWeldingDetector bằng Python thường."""
    tests = [
        test_levels,
        test_finite_line_intersection_count,
        test_json_coordinates_are_used_to_measure,
        test_measurement_and_slit_share_polygon_per_run,
        test_retrain_inputs_are_saved_per_inspector,
        test_run_summary_saves_input_before_model_call,
        test_invalid_runtime_line_is_ng,
    ]
    for test in tests:
        print(f"\n===== {test.__name__} =====")
        test()
        print("PASS")
    print(f"\nĐã chạy {len(tests)} test MeasurementWeldingDetector: PASS")


if __name__ == "__main__":
    main()
