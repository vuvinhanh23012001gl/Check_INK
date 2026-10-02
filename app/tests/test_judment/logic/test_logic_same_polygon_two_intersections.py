import sys
from pathlib import Path
from unittest.mock import Mock

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.judger import BorderDetector


def test_line_crosses_two_polygons_one_point_each_must_be_invalid() -> None:
    """Xac nhan rule do line: phai co 2 giao diem tren cung mot polygon.

    Input:
        - Hai polygon tach roi dang hinh chu nhat.
        - Mot line co diem dau nam trong polygon 1 va diem cuoi nam trong polygon 2.
          Do do moi polygon chi co 1 giao diem voi bien.
    Output:
        - Runtime line phai co ``intersection_count=1`` va ``is_valid=False``.
        - ``distance_pixel`` phai bang 0.0 vi khong du 2 giao diem tren cung contour.
    Errors:
        - AssertionError neu detector do duoc khoang cach trong case khong hop le.
    """
    dummy_unet = Mock()
    detector = BorderDetector(dummy_unet)
    image = np.zeros((300, 300, 3), dtype=np.uint8)

    polygon_left = np.array(
        [[[0, 0]], [[100, 0]], [[100, 100]], [[0, 100]]],
        dtype=np.int32,
    )
    polygon_right = np.array(
        [[[120, 0]], [[220, 0]], [[220, 100]], [[120, 100]]],
        dtype=np.int32,
    )

    # Diem dau trong polygon trai, diem cuoi trong polygon phai.
    # Khi xet tung polygon rieng le, line chi cat bien mot lan.
    lines = [(50.0, 50.0, 170.0, 50.0)]

    runtime = detector.define_with_polygon(
        image=image,
        lines=lines,
        polygon=polygon_left,
        polygons=[polygon_left, polygon_right],
    )

    assert isinstance(runtime, dict)
    assert "lines" in runtime and len(runtime["lines"]) == 1

    line_result = runtime["lines"][0]
    assert line_result["intersection_count"] == 1
    assert line_result["is_valid"] is False
    assert line_result["distance_pixel"] == 0.0


def main() -> None:
    """Chay test logic cho quy tac 2 giao diem tren cung polygon.

    Input: Khong co.
    Output: In PASS neu test dat.
    Errors: AssertionError neu ket qua sai voi quy tac mong doi.
    """
    test_line_crosses_two_polygons_one_point_each_must_be_invalid()
    print("PASS: test_line_crosses_two_polygons_one_point_each_must_be_invalid")


if __name__ == "__main__":
    main()
