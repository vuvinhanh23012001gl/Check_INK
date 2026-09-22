import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PATH_FILE_MODEL_YOLO_STRUCTURE, YoloDetectObjectConfig
from app.engines.AI_model_process import FrameModelYoloObject
from app.engines.model_AI import ModelYoloObject
from app.judger import HoleDetector


# Cấu hình chạy model YOLO thật. Có thể thay ảnh, ROI và chuẩn ở đây.
MODEL_PATH = PATH_FILE_MODEL_YOLO_STRUCTURE
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "1.jpg"
STANDARD_DATA = True
X1 = 854
Y1 = 314
X2 = 1957
Y2 = 1237


def main():
    """Chạy HoleDetector với model YOLO và ảnh thật.

    Input: Các hằng số model, ảnh, chuẩn và ROI ở đầu file.
    Output: ``JudgmentResult`` được in ra console.
    Errors: FileNotFoundError nếu thiếu model/ảnh; RuntimeError nếu không đọc
        được ảnh hoặc model trả output không hợp lệ.
    """
    print("===== CHẠY THỰC TẾ HOLE =====")
    print("Model:", MODEL_PATH)
    print("Ảnh:", IMAGE_PATH)
    print("standard_data:", STANDARD_DATA)

    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"Không tìm thấy model: {MODEL_PATH}")
    image_path = Path(IMAGE_PATH)
    if not image_path.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {IMAGE_PATH}")

    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Không đọc được ảnh: {IMAGE_PATH}")

    x2 = image.shape[1] if X2 is None else X2
    y2 = image.shape[0] if Y2 is None else Y2
    print(f"ROI: x1={X1}, y1={Y1}, x2={x2}, y2={y2}")

    print("\n[1] Khởi tạo model YOLO thật...")
    config = YoloDetectObjectConfig(
        path_model=str(model_path),
        device="cpu",
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )
    model = ModelYoloObject(config)
    frame_model = FrameModelYoloObject(model)
    detector = HoleDetector(frame_model)
    print("Model đã load và warmup xong.")

    print("\n[2] Chạy define() để nhận diện Hole...")
    runtime_data = detector.define(image, X1, Y1, x2, y2)
    status, messages, image_result, objects = runtime_data
    print("  status:", status)
    print("  messages:", messages)
    print("  image_result:", image_result.shape if image_result is not None else None)
    print("  objects:", objects)
    print("  số object:", len(objects))

    print("\n[3] Chạy compare()...")
    comparison_data = detector.compare(STANDARD_DATA, runtime_data)
    print("  standard_exists:", comparison_data["standard_exists"])
    print("  runtime_exists:", comparison_data["runtime_exists"])
    print("  runtime_count:", comparison_data["runtime_count"])

    print("\n[4] Chạy judge()...")
    result = detector.judge(comparison_data)
    print("  status:", result.status)
    print("  ok:", result.ok)
    print("  message:", result.message)
    print("  errors:", result.errors)
    print("\n===== KẾT THÚC =====")
    print("KẾT QUẢ:", result.status)
    return result


if __name__ == "__main__":
    main()
