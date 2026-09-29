"""Kiểm thử chuyên sâu cho ForeignObjectDetector (Phán định Dị vật).

Bao gồm:
1. TestForeignObjectDetectorLogic: Kiểm thử đơn vị (Unit Test) cho toàn bộ các nhánh logic
   phán định theo chuẩn BaseJudgerAI (OK khi <= ngưỡng, OK khi > ngưỡng nhưng không có dị vật,
   NG khi > ngưỡng và có dị vật).
2. test_real_foreign_object_runtime: Kiểm thử thời gian thực (Runtime Test) kết hợp cả mô hình
   PatchCore thật và mô hình YOLO Object thật trên ảnh thực tế trong cơ sở dữ liệu.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple
import unittest
from unittest.mock import MagicMock

import cv2
import numpy as np

# Đảm bảo đường dẫn import tương đối chuẩn xác từ thư mục gốc
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PatchCoreAnomalyConfig, YoloDetectObjectConfig
from app.engines.AI_model_process import (
    FrameModelPatchCore,
    FramePatchCoreObjectDetector,
)
from app.engines.model_AI import ModelPatchCore, ModelYoloObject
from app.judger import ForeignObjectDetector, JudgmentResult


class TestForeignObjectDetectorLogic(unittest.TestCase):
    """Kiểm thử đơn vị logic phán định độc lập của ForeignObjectDetector."""

    def setUp(self) -> None:
        """Thiết lập môi trường mock trước mỗi bài kiểm tra."""
        self.mock_model = MagicMock(spec=FramePatchCoreObjectDetector)
        self.detector = ForeignObjectDetector(self.mock_model)
        self.dummy_image = np.zeros((400, 400, 3), dtype=np.uint8)
        self.x1, self.y1, self.x2, self.y2 = 50, 50, 250, 250

    def test_init_validation(self) -> None:
        """Kiểm tra khởi tạo detector với model không đúng chuẩn hợp đồng."""
        with self.assertRaises(TypeError):
            ForeignObjectDetector(object())  # type: ignore

    def test_define_calls_model_with_threshold(self) -> None:
        """Kiểm tra define truyền chính xác tham số threshold xuống engine model."""
        self.mock_model.detect_anomaly_objects_with_heatmap.return_value = {
            "score": 0.12,
            "heatmap": None,
            "detections": [],
            "anomaly_boxes": [],
        }

        runtime_data = self.detector.define(
            self.dummy_image, self.x1, self.y1, self.x2, self.y2, threshold=0.25
        )

        self.mock_model.detect_anomaly_objects_with_heatmap.assert_called_once_with(
            self.dummy_image, self.x1, self.y1, self.x2, self.y2, threshold=0.25
        )
        self.assertAlmostEqual(runtime_data["score"], 0.12)
        self.assertEqual(runtime_data["detections"], [])
        self.assertIn("image", runtime_data)
        self.assertIn("anomaly_boxes", runtime_data)

    def test_case_1_score_less_than_or_equal_threshold_is_ok(self) -> None:
        """Nhánh 1: Score bất thường runtime <= threshold cài đặt -> Kết quả ĐẠT (OK)."""
        runtime_data = {
            "score": 0.15,
            "heatmap": None,
            "detections": [],
            "anomaly_boxes": [],
            "roi": {"x1": 50, "y1": 50, "x2": 250, "y2": 250},
            "image": self.dummy_image,
        }

        comparison_data = self.detector.compare(
            standard_data={"threshold": 0.20}, runtime_data=runtime_data
        )
        result = self.detector.judge(comparison_data)

        self.assertTrue(result.ok)
        self.assertEqual(result.status, "OK")
        self.assertEqual(len(result.errors), 0)
        self.assertIn("ĐẠT chuẩn", result.message)

    def test_case_2_score_greater_than_threshold_without_yolo_detections_is_ok(self) -> None:
        """Nhánh 2: Score > threshold nhưng YOLO KHÔNG phát hiện dị vật -> Kết quả ĐẠT (OK)."""
        runtime_data = {
            "score": 0.35,
            "heatmap": None,
            "detections": [],  # YOLO đã quét các vùng heatmap nhưng không thấy dị vật
            "anomaly_boxes": [(60, 60, 30, 30)],
            "roi": {"x1": 50, "y1": 50, "x2": 250, "y2": 250},
            "image": self.dummy_image,
        }

        comparison_data = self.detector.compare(
            standard_data={"threshold": 0.20}, runtime_data=runtime_data
        )
        result = self.detector.judge(comparison_data)

        self.assertTrue(result.ok)
        self.assertEqual(result.status, "OK")
        self.assertEqual(len(result.errors), 0)
        self.assertIn("không phát hiện dị vật YOLO: ĐẠT chuẩn", result.message)

    def test_case_3_score_greater_than_threshold_with_yolo_detections_is_ng(self) -> None:
        """Nhánh 3: Score > threshold và YOLO CÓ phát hiện dị vật -> Kết quả LỖI (NG)."""
        fake_detections = [
            {
                "class_id": 0,
                "class_name": "ForeignObject",
                "confidence": 0.85,
                "bbox": {"x1": 80, "y1": 80, "x2": 120, "y2": 120},
            }
        ]
        runtime_data = {
            "score": 0.40,
            "heatmap": None,
            "detections": fake_detections,
            "anomaly_boxes": [(70, 70, 60, 60)],
            "roi": {"x1": 50, "y1": 50, "x2": 250, "y2": 250},
            "image": self.dummy_image,
        }

        comparison_data = self.detector.compare(
            standard_data={"threshold": 0.20}, runtime_data=runtime_data
        )
        result = self.detector.judge(comparison_data)

        self.assertFalse(result.ok)
        self.assertEqual(result.status, "NG")
        self.assertEqual(len(result.errors), 1)
        self.assertIn("phát hiện 1 dị vật bất thường", result.message)
        self.assertEqual(result.runtime_data["detections_count"], 1)

    def test_standard_data_parsing_flexibility(self) -> None:
        """Kiểm tra khả năng tương thích với nhiều kiểu dữ liệu standard_data."""
        runtime_data = {"score": 0.25, "detections": []}

        # Dạng số thực float
        r1 = self.detector.compare(0.30, runtime_data)
        self.assertEqual(r1["standard_threshold"], 0.30)
        self.assertTrue(r1["ok"])

        # Dạng dict phẳng
        r2 = self.detector.compare({"threshold": 0.20}, runtime_data)
        self.assertEqual(r2["standard_threshold"], 0.20)
        self.assertTrue(r2["ok"])  # detections rỗng nên OK

        # Dạng dict cấu hình từ config_judgment_law.json
        r3 = self.detector.compare(
            {"ForeignObjectInspector": {"threshold": 0.18}}, runtime_data
        )
        self.assertEqual(r3["standard_threshold"], 0.18)

    def test_full_evaluate_workflow(self) -> None:
        """Kiểm tra toàn bộ chu trình chuẩn evaluate(): define -> compare -> judge."""
        self.mock_model.detect_anomaly_objects_with_heatmap.return_value = {
            "score": 0.08,
            "heatmap": None,
            "detections": [],
            "anomaly_boxes": [],
        }

        result = self.detector.evaluate(
            standard_data={"threshold": 0.20},
            img=self.dummy_image,
            x1=self.x1,
            y1=self.y1,
            x2=self.x2,
            y2=self.y2,
            threshold=0.20,
        )

        self.assertIsInstance(result, JudgmentResult)
        self.assertTrue(result.ok)
        self.assertEqual(result.status, "OK")


def test_real_foreign_object_runtime() -> None:
    """Kiểm thử thời gian thực với mô hình PatchCore + YOLO Object thật trên ảnh thực tế."""
    print("\n" + "=" * 70)
    print("▶ BẮT ĐẦU RUNTIME TEST: PHÁN ĐỊNH DỊ VẬT (FOREIGN OBJECT DETECTOR)")
    print("=" * 70)

    patchcore_index_path = (
        PROJECT_ROOT
        / "app"
        / "input"
        / "model"
        / "patch_core"
        / "1"
        / "0"
        / "0"
        / "model_foreign_crop_20260928_084358_179299"
        / "the_first"
        / "patchcore.index"
    )
    yolo_model_path = (
        PROJECT_ROOT
        / "model_air_bubble"
        / "train16"
        / "weights"
        / "best.pt"
    )
    image_path = (
        PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "0.jpg"
    )

    if not patchcore_index_path.exists():
        print(f"⚠️ Bỏ qua test runtime: Không tìm thấy index PatchCore tại: {patchcore_index_path}")
        return

    if not yolo_model_path.exists():
        print(f"⚠️ Bỏ qua test runtime: Không tìm thấy weights YOLO tại: {yolo_model_path}")
        return

    if not image_path.exists():
        print(f"⚠️ Bỏ qua test runtime: Không tìm thấy ảnh tại: {image_path}")
        return

    # 1. Nạp ảnh kiểm tra thực tế
    image = cv2.imread(str(image_path))
    assert image is not None, f"Không đọc được ảnh tại {image_path}"
    print(f"1. Đã nạp ảnh thực tế: {image_path.name} (kích thước {image.shape})")

    # 2. Khởi tạo mô hình PatchCore
    print("2. Đang nạp mô hình PatchCore...")
    patchcore_config = PatchCoreAnomalyConfig(
        index_path=str(patchcore_index_path),
        nprobe=10,
        img_size=256,
        device="cpu",
    )
    model_patchcore = ModelPatchCore(patchcore_config)
    model_patchcore.load_model()
    model_patchcore.warmup()
    frame_patchcore = FrameModelPatchCore(model_patchcore)

    # 3. Khởi tạo mô hình YOLO Object
    print("3. Đang nạp mô hình YOLO Object...")
    yolo_config = YoloDetectObjectConfig(
        path_model=str(yolo_model_path),
        device="cpu",
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )
    model_yolo = ModelYoloObject(yolo_config)
    model_yolo.load_model()
    model_yolo.warmup()

    # 4. Khởi tạo detector
    detector_engine = FramePatchCoreObjectDetector(
        patch_core_frame=frame_patchcore,
        yolo_object_model=model_yolo,
    )
    foreign_detector = ForeignObjectDetector(detector_engine)
    print("4. Đã khởi tạo ForeignObjectDetector hoàn tất.")

    # 5. Thông số cấu hình ROI kiểm tra
    x1, y1, x2, y2 = 818, 378, 1596, 942
    threshold_config = 0.20

    print(f"\n5. Thực thi phán định runtime:")
    print(f"   - Vùng đưa vào PatchCore kiểm tra bất thường (ROI): x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    print(f"   - Ngưỡng bất thường cài đặt (threshold): {threshold_config}")

    result = foreign_detector.evaluate(
        standard_data={"threshold": threshold_config},
        img=image,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
        threshold=threshold_config,
    )

    print("\n" + "-" * 40)
    print("📊 KẾT QUẢ PHÁN ĐỊNH RUNTIME CHI TIẾT")
    print("-" * 40)
    print(f"• Trạng thái (status): {result.status} (ok={result.ok})")
    print(f"• Điểm bất thường cao nhất (score): {result.runtime_data['score']:.4f}")
    anomaly_boxes = result.runtime_data.get("anomaly_boxes", [])
    print(f"• Số vùng heatmap bất thường vượt ngưỡng: {len(anomaly_boxes)}")
    for i, box in enumerate(anomaly_boxes, start=1):
        print(f"    [Vùng {i}] x={box[0]}, y={box[1]}, w={box[2]}, h={box[3]}")

    detections = result.runtime_data.get("detections", [])
    print(f"• Số dị vật YOLO nhận diện trong các vùng bất thường: {len(detections)}")
    for i, det in enumerate(detections, start=1):
        print(
            f"    - Dị vật {i}: class={det.get('class_name')} "
            f"conf={det.get('confidence'):.3f} bbox={det.get('bbox')}"
        )
    print(f"• Thông điệp đánh giá: {result.message}")

    # 6. Lưu ảnh kết quả trực quan
    output_dir = PROJECT_ROOT / "app" / "output" / "test_foreign_object_detector"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_img_path = output_dir / "result_runtime_foreign_object.jpg"
    cv2.imwrite(str(out_img_path), result.runtime_data["image"])
    print(f"\n✅ Đã lưu ảnh kết quả trực quan tại: {out_img_path}")
    print("=" * 70)


if __name__ == "__main__":
    # 1. Chạy bài kiểm tra đơn vị (Unit Test Logic)
    print("\n🔍 ĐANG CHẠY BỘ KIỂM TRA ĐƠN VỊ (UNIT TEST LOGIC)...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestForeignObjectDetectorLogic)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    if not test_result.wasSuccessful():
        print("❌ Kiểm tra đơn vị thất bại!")
        sys.exit(1)

    print("✅ TẤT CẢ CÁC TEST LOGIC ĐỀU VƯỢT QUA!")

    # 2. Chạy bài kiểm tra thời gian thực (Runtime Test)
    test_real_foreign_object_runtime()
