import unittest

import numpy as np

from app.engines.service.surface_fram_yolo_service import SurfaceFrameYoloService


class FakeFrameModel:
    def __init__(self, objects):
        self.objects = objects

    def get_objects(self, image, x1, y1, x2, y2):
        return self.objects, None

    @staticmethod
    def filter_objects_by_class_name(objects, class_name):
        return objects, None


class TestSurfaceFrameYoloService(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.regions = [{"id": 0, "xStart": 0, "yStart": 0, "xEnd": 50, "yEnd": 50}]

    def test_missing_weld_polygon_only_reports_detection(self):
        model = FakeFrameModel([{
            "bbox": {"x1": 10, "y1": 10, "x2": 20, "y2": 20},
            "confidence": 0.9,
        }])
        service = SurfaceFrameYoloService(model)

        result = service.judge_regions(self.image, self.regions, 100)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"], "DETECT_ONLY")
        self.assertIsNone(result.data["is_ok"])
        self.assertIsNone(result.data["inside_weld_count"])
        self.assertIsNone(result.data["outside_weld_count"])
        self.assertIsNone(result.data["objects"][0]["is_inside_weld"])
        self.assertEqual(result.data["objects"][0]["location_text"], "Chưa đánh giá")
        self.assertIsNone(result.data["regions"][0]["ok"])

    def test_missing_weld_polygon_with_no_bubbles_is_not_ok_judgment(self):
        service = SurfaceFrameYoloService(FakeFrameModel([]))

        result = service.judge_regions(self.image, self.regions, 100)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"], "DETECT_ONLY")
        self.assertIsNone(result.data["is_ok"])
        self.assertFalse(result.data["objects"])

    def test_weld_polygon_keeps_ok_ng_judgment(self):
        model = FakeFrameModel([{
            "bbox": {"x1": 10, "y1": 10, "x2": 20, "y2": 20},
            "confidence": 0.9,
        }])
        service = SurfaceFrameYoloService(model)
        polygon = [[[0, 0], [30, 0], [30, 30], [0, 30]]]

        result = service.judge_regions(self.image, self.regions, 100, polygon)

        self.assertTrue(result.ok)
        self.assertEqual(result.data["status"], "NG")
        self.assertFalse(result.data["is_ok"])
        self.assertEqual(result.data["inside_weld_count"], 1)
        self.assertEqual(result.data["objects"][0]["location_text"], "Trong đường hàn")


if __name__ == "__main__":
    unittest.main()