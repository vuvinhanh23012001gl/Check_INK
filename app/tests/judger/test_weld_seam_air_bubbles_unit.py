import numpy as np
from unittest.mock import MagicMock
from app.judger.weld_seam_air_bubbles_detector import WeldSeamAirBubbles
from app.services.weld_reference_service import WeldReferenceService
from app.services.judment_law_product_service import JudmentLawProductSevice
from app.config import ClassNameModelSurfaceConfig


class DummyYoloBubbleModel:
    """Mock FrameModelYoloObject để test logic phân loại bọt khí."""

    def __init__(self, detected_objects=None):
        self.detected_objects = detected_objects or []

    def get_objects(self, img, x1, y1, x2, y2):
        return self.detected_objects, img[y1:y2, x1:x2]

    def filter_objects_by_class_name(self, objects, class_name):
        filtered = [
            obj for obj in objects
            if obj.get("class_name", "").lower() == class_name.lower()
        ]
        return filtered, len(filtered) > 0

    def draw(self, img, objects):
        return img.copy()


def mock_weld_polygon():
    """Tạo polygon đường hàn dạng hình chữ nhật [100, 100] đến [300, 300]."""
    return [
        [[100, 100], [300, 100], [300, 300], [100, 300]]
    ]


def test_weld_reference_service(tmp_path):
    """Kiểm tra lưu trữ và truy xuất bản ghi tham chiếu đường hàn."""
    service = WeldReferenceService()
    service.STORAGE_DIR = tmp_path / "weld_ref"
    service.RECORD_CATALOG_FILE = tmp_path / "weld_ref_catalog.json"
    service.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    record_id = service.generate_record_id(1, 0, 0)
    assert record_id == "weld_ref_p1_f0_i0"

    polygon = [[[50, 50], [150, 50], [150, 150], [50, 150]]]
    skeleton = [[100, 60], [100, 100], [100, 140]]

    success = service.save_reference(
        record_id=record_id,
        product_id=1,
        frame_id=0,
        item_id=0,
        polygon=polygon,
        skeleton=skeleton,
        width=2048,
        height=1536,
    )
    assert success is True

    ref_data = service.get_reference(record_id)
    assert ref_data is not None
    assert ref_data["id"] == record_id
    assert len(ref_data["polygon"]) == 1
    assert len(ref_data["skeleton"]) == 3
    assert ref_data["metadata"]["image_width"] == 2048

    contour = service.get_polygon_contour(record_id)
    assert contour is not None
    assert len(contour) == 4


def test_weld_seam_air_bubbles_no_bubble(mock_weld_polygon):
    """TH1: Không có bọt khí nào -> Kết quả OK, thông báo 'Không phát hiện bọt khí'."""
    yolo_mock = DummyYoloBubbleModel(detected_objects=[])
    detector = WeldSeamAirBubbles(model_bubble=yolo_mock)

    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    regions = [(50, 50, 300, 300)]

    is_valid, messages, img_out, metadata = detector.define(dummy_img, regions, weld_polygon=mock_weld_polygon)
    assert is_valid is True
    assert metadata["has_runtime_polygon"] is True

    comp_data = detector.compare(True, (is_valid, messages, img_out, metadata))
    judg_res = detector.judge(comp_data)

    assert judg_res.ok is True
    assert judg_res.status == "OK"
    assert judg_res.message == "Không phát hiện bọt khí"
    assert len(judg_res.errors) == 0


def test_weld_seam_air_bubbles_inside_weld(mock_weld_polygon):
    """TH2: Có bọt khí nằm TRONG đường hàn -> Kết quả NG, 'Phát hiện bọt khí trong đường hàn'."""
    # Bọt khí tại tâm (200, 200) nằm bên trong polygon [100, 100] đến [300, 300]
    detected_inside = [{
        "class_name": ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
        "confidence": 0.95,
        "bbox": {"x1": 190, "y1": 190, "x2": 210, "y2": 210},
    }]
    yolo_mock = DummyYoloBubbleModel(detected_objects=detected_inside)
    detector = WeldSeamAirBubbles(model_bubble=yolo_mock)

    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    regions = [(50, 50, 300, 300)]

    is_valid, messages, img_out, metadata = detector.define(dummy_img, regions, weld_polygon=mock_weld_polygon)
    assert is_valid is False
    assert any("trong đường hàn" in m for m in messages)
    assert metadata["inside_count"] == 1

    comp_data = detector.compare(True, (is_valid, messages, img_out, metadata))
    judg_res = detector.judge(comp_data)

    assert judg_res.ok is False
    assert judg_res.status == "NG"
    assert "trong đường hàn" in judg_res.message
    assert len(judg_res.errors) == 1
    assert "🔵 [Bọt khí đường hàn] NG" in judg_res.errors[0]
    assert "Phát hiện bọt khí trong đường hàn" in judg_res.errors[0]


def test_weld_seam_air_bubbles_outside_weld(mock_weld_polygon):
    """TH3: Có bọt khí nằm NGOÀI đường hàn -> Kết quả OK, chỉ cảnh báo."""
    # Bọt khí tại (60, 60) nằm bên ngoài polygon [100, 100] đến [300, 300]
    detected_outside = [{
        "class_name": ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
        "confidence": 0.88,
        "bbox": {"x1": 50, "y1": 50, "x2": 70, "y2": 70},
    }]
    yolo_mock = DummyYoloBubbleModel(detected_objects=detected_outside)
    detector = WeldSeamAirBubbles(model_bubble=yolo_mock)

    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    regions = [(40, 40, 320, 320)]

    is_valid, messages, img_out, metadata = detector.define(dummy_img, regions, weld_polygon=mock_weld_polygon)
    assert is_valid is False
    assert any("ngoài đường hàn" in m for m in messages)
    assert metadata["outside_count"] == 1

    comp_data = detector.compare(True, (is_valid, messages, img_out, metadata))
    judg_res = detector.judge(comp_data)

    assert judg_res.ok is True
    assert judg_res.status == "OK"
    assert "ngoài đường hàn" in judg_res.message
    assert "cảnh báo" in judg_res.message.lower()
    assert len(judg_res.errors) == 0


def test_convert_canvas_coordinates_with_weld_reference():
    """Kiểm tra convert_canvas_coordinates không lỗi khi gặp weld_reference_id hoặc weld_data."""
    repo_mock = MagicMock()
    service = JudmentLawProductSevice(repo=repo_mock)

    point_service_mock = MagicMock()
    # Mock đọc ảnh kích thước 1000x800
    mock_img = np.zeros((800, 1000, 3), dtype=np.uint8)
    point_service_mock.get_path_img_point.return_value = MagicMock(ok=True, data="mock_path.jpg")

    import cv2
    orig_imread = cv2.imread
    cv2.imread = lambda path: mock_img

    try:
        data = {
            "1": {
                "0": {
                    "0": {
                        "AirBubblesItemInspector": {
                            "0": {
                                "id": 0,
                                "name": "Vùng 1",
                                "xStart": 100,
                                "yStart": 100,
                                "xEnd": 200,
                                "yEnd": 200,
                            },
                            "weld_reference_id": "weld_ref_p1_f0_i0",
                            "weld_data": {"polygon": [], "skeleton": []}
                        }
                    }
                }
            }
        }
        res = service.convert_canvas_coordinates(
            data=data,
            product_id=1,
            point_service=point_service_mock,
            canvas_width=1000,
            canvas_height=800,
        )
        assert res.ok is True
        insp = res.data["1"]["0"]["0"]["AirBubblesItemInspector"]
        assert insp["weld_reference_id"] == "weld_ref_p1_f0_i0"
        assert insp["0"]["coordinateSpace"] == "image"
    finally:
        cv2.imread = orig_imread


def test_weld_seam_air_bubbles_missing_polygon_is_ng_no_data():
    """Thiếu polygon runtime phải trả OK theo nguyên tắc hiện tại."""
    detected_inside = [{
        "class_name": ClassNameModelSurfaceConfig.AIR_BUBBLE.value,
        "confidence": 0.95,
        "bbox": {"x1": 190, "y1": 190, "x2": 210, "y2": 210},
    }]
    yolo_mock = DummyYoloBubbleModel(detected_objects=detected_inside)
    detector = WeldSeamAirBubbles(model_bubble=yolo_mock)

    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    regions = [(50, 50, 300, 300)]

    is_valid, messages, img_out, metadata = detector.define(dummy_img, regions, weld_polygon=None)
    assert is_valid is False
    assert metadata["missing_runtime_polygon"] is True

    comp_data = detector.compare(True, (is_valid, messages, img_out, metadata))
    judg_res = detector.judge(comp_data)

    assert judg_res.ok is True
    assert judg_res.status == "OK"
    assert judg_res.runtime_data["missing_judgment_data"] is False
    assert "Không có polygon runtime" in judg_res.message


def test_weld_seam_air_bubbles_normalize_ndarray_skeleton_points():
    """Fallback UNet trả ndarray skeleton phải được chuẩn hóa để vẽ và serialize."""
    yolo_mock = DummyYoloBubbleModel(detected_objects=[])
    detector = WeldSeamAirBubbles(model_bubble=yolo_mock)

    class DummyWeldService:
        def extract_weld_seam_reference(self, img):
            polygons = [[[100, 100], [300, 100], [300, 300], [100, 300]]]
            centers = np.array([[10.2, 20.7], [30.0, 40.0]], dtype=np.float32)
            return polygons, centers, None

    detector.set_weld_seam_service(DummyWeldService())

    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    regions = [(50, 50, 300, 300)]

    _, _, _, metadata = detector.define(dummy_img, regions, weld_polygon=None)
    assert metadata["skeleton_points"] == [[10, 21], [30, 40]]

    comp_data = detector.compare(True, (True, [], dummy_img, metadata))
    assert comp_data["skeleton_points"] == [[10, 21], [30, 40]]


if __name__ == "__main__":
    import tempfile
    import pathlib
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_weld_reference_service(pathlib.Path(tmp_dir))
        print("✓ test_weld_reference_service PASSED")

    poly = [[[100, 100], [300, 100], [300, 300], [100, 300]]]
    test_weld_seam_air_bubbles_no_bubble(poly)
    print("✓ test_weld_seam_air_bubbles_no_bubble PASSED")

    test_weld_seam_air_bubbles_inside_weld(poly)
    print("✓ test_weld_seam_air_bubbles_inside_weld PASSED")

    test_weld_seam_air_bubbles_outside_weld(poly)
    print("✓ test_weld_seam_air_bubbles_outside_weld PASSED")

    test_convert_canvas_coordinates_with_weld_reference()
    print("✓ test_convert_canvas_coordinates_with_weld_reference PASSED")

    test_weld_seam_air_bubbles_missing_polygon_is_ng_no_data()
    print("✓ test_weld_seam_air_bubbles_missing_polygon_is_ng_no_data PASSED")

    test_weld_seam_air_bubbles_normalize_ndarray_skeleton_points()
    print("✓ test_weld_seam_air_bubbles_normalize_ndarray_skeleton_points PASSED")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

