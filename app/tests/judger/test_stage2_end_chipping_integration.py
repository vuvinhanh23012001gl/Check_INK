import json
import unittest
from pathlib import Path
import numpy as np

from app.config.path_config import PATH_FILE_DATA_CONFIG_JUDMENT_LAW
from app.judger import Judment, EndChippingDetector


class DummyPointService:
    def get_path_img_point(self, product_id, frame_id, item_id):
        class DummyRes:
            ok = True
            data = Path("dummy.png")
        return DummyRes()


class DummyPatchCoreFrame:
    def predict_with_anomaly_boxes(self, img, x1, y1, x2, y2, threshold=0.1, min_area=50):
        # Giả lập trả về score 0.05, heatmap giả, và không có box bất thường nếu score <= threshold
        h, w = y2 - y1, x2 - x1
        heatmap = np.zeros((h, w, 3), dtype=np.uint8)
        boxes = []
        return 0.05, heatmap, boxes


class DummyEndChippingService:
    def get_patchcore_frame(self, product_id, frame_id, item_id):
        return DummyPatchCoreFrame()


class TestEndChippingIntegration(unittest.TestCase):
    def test_judment_registry_contains_end_chipping(self):
        detector = EndChippingDetector(end_chipping_service=DummyEndChippingService())
        judment = Judment({
            "EndChippingInspector": detector
        })

        # Đọc cấu hình thực tế
        with open(PATH_FILE_DATA_CONFIG_JUDMENT_LAW, "r", encoding="utf-8") as f:
            full_config = json.load(f)

        item_config = full_config.get("2", {}).get("0", {}).get("0", {})
        self.assertIn("EndChippingInspector", item_config)

        # Kiểm tra Judment._tasks_from_config không văng lỗi thiếu detector
        tasks = judment._tasks_from_config(
            item_config,
            inspector_registry=judment.inspector_registry,
            scale_mm_per_pixel=1.0,
            context={"product_id": 2, "frame_id": 0, "item_id": 0},
        )
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].inspector.INSPECTOR_NAME, "EndChippingInspector")
        self.assertEqual(tasks[0].define_kwargs.get("threshold"), 0.1)

        # Kiểm tra chạy run_summary không bị lỗi chưa có detector
        img = np.zeros((600, 2000, 3), dtype=np.uint8)
        summary = judment.run_summary(
            img,
            item_config,
            training_context={"product_id": "2", "frame_id": "0", "item_id": "0"}
        )
        self.assertNotIn("Chưa có detector cho inspector 'EndChippingInspector'", str(summary))

    def test_end_chipping_detector_define_and_judge(self):
        detector = EndChippingDetector(end_chipping_service=DummyEndChippingService())
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Test define
        runtime_data = detector.define(
            img,
            x1=100, y1=50, x2=300, y2=250,
            threshold=0.1,
            product_id=2, frame_id=0, item_id=0,
        )
        self.assertIn("score", runtime_data)
        self.assertIn("image", runtime_data)
        self.assertEqual(runtime_data["score"], 0.05)

        # Test compare & judge khi OK
        comp = detector.compare(0.1, runtime_data)
        self.assertTrue(comp["ok"])
        res = detector.judge(comp)
        self.assertTrue(res.ok)
        self.assertEqual(res.status, "OK")


if __name__ == "__main__":
    unittest.main()
