import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PATH_FILE_MODEL_YOLO_SURFACE, YoloDetectObjectConfig
from app.engines.AI_model_process import FrameModelYoloObject
from app.engines.model_AI import ModelYoloObject
from app.judger import ScratchThePipeDetector


# Cấu hình chạy model YOLO thật. Có thể thay ảnh, ROI ở đây.
MODEL_PATH = PATH_FILE_MODEL_YOLO_SURFACE
IMAGE_PATH = (
    PROJECT_ROOT
    / "storage"
    / "img_points"
    / "1"
    / "0"
    / "4.jpg"
)
X1 = 0
Y1 = 0
X2 = None
Y2 = None


def main():
    """Chạy ScratchThePipeDetector với model YOLO surface và ảnh thật.

    Input: Các hằng số model, ảnh và ROI ở đầu file.
    Output: ``JudgmentResult`` được in ra console.
    Errors: FileNotFoundError nếu thiếu model/ảnh; RuntimeError nếu không đọc
        được ảnh hoặc model trả output không hợp lệ.
    """
    print("===== CHẠY THỰC TẾ SCRATCH THE PIPE =====")
    print("Model:", MODEL_PATH)
    print("Ảnh:", IMAGE_PATH)

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

    config = YoloDetectObjectConfig(
        path_model=str(model_path),
        device="cpu",
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )
    model = ModelYoloObject(config)
    frame_model = FrameModelYoloObject(model)
    detector = ScratchThePipeDetector(frame_model)
    print("Model đã load và warmup xong.")

    runtime_data = detector.define(image, X1, Y1, x2, y2)
    status, messages, image_result = runtime_data
    print("status:", status)
    print("messages:", messages)
    print("image_result:", image_result.shape if image_result is not None else None)

    result = detector.compare(True, runtime_data)
    result = detector.judge(result)
    print("judgment:", result.to_dict())
    print("KẾT QUẢ:", result.status)
    print("Đang mở ảnh kết quả. Nhấn phím bất kỳ trên cửa sổ ảnh để kết thúc.")
    frame_model.show(image_result, window_name="Scratch The Pipe Result")
    return result


if __name__ == "__main__":
    main()
