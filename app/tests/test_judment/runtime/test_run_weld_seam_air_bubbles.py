import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import YoloDetectObjectConfig
from app.engines.AI_model_process import FrameModelYoloObject
from app.engines.model_AI import ModelYoloObject
from app.judger import WeldSeamAirBubbles


MODEL_PATH = PROJECT_ROOT / "model_air_bubble" / "train16" / "weights" / "best.pt"
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "1.jpg"
OUTPUT_PATH = PROJECT_ROOT / "app" / "output" / "weld_seam_air_bubbles_result.jpg"
# Box dạng (x, y, width, height), theo pixel ảnh thật.
ABNORMAL_REGIONS = [(0, 0, 2048, 1536)]


def main():
    """Chạy WeldSeamAirBubbles với model YOLO và ảnh thật.

    Input: MODEL_PATH, IMAGE_PATH và ABNORMAL_REGIONS ở đầu file.
    Output: In số vùng, trạng thái từng bước và lưu ảnh kết quả.
    Errors: FileNotFoundError nếu thiếu model/ảnh; RuntimeError nếu ảnh hoặc
        model không hợp lệ.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy model bọt khí: {MODEL_PATH}")
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {IMAGE_PATH}")

    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise RuntimeError(f"Không đọc được ảnh: {IMAGE_PATH}")

    regions = [(0, 0, image.shape[1], image.shape[0])]
    config = YoloDetectObjectConfig(
        path_model=str(MODEL_PATH),
        device="cpu",
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )
    model = ModelYoloObject(config)
    frame_model = FrameModelYoloObject(model)
    detector = WeldSeamAirBubbles(frame_model)

    runtime_data = detector.define(image, regions)
    comparison_data = detector.compare(True, runtime_data)
    result = detector.judge(comparison_data)

    print("===== WELD SEAM AIR BUBBLES =====")
    print("model:", MODEL_PATH)
    print("image:", IMAGE_PATH)
    print("status:", runtime_data[0])
    print("messages:")
    for message in runtime_data[1]:
        print(" -", message)
    print("judgment:", result.status)
    print("message:", result.message)
    print("errors:", result.errors)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT_PATH), runtime_data[2]):
        raise RuntimeError(f"Không lưu được ảnh kết quả: {OUTPUT_PATH}")
    print("result image:", OUTPUT_PATH)

    display_image = runtime_data[2].copy()
    for x, y, width, height in regions:
        cv2.rectangle(
            display_image,
            (int(x), int(y)),
            (int(x + width), int(y + height)),
            (255, 0, 0),
            3,
        )
        cv2.putText(
            display_image,
            "WELD SEAM SCAN ZONE",
            (int(x) + 10, max(30, int(y) + 35)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

    window_name = "Weld Seam Air Bubbles Result"
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        image_height, image_width = display_image.shape[:2]
        max_width = 1400
        if image_width > max_width:
            resize_ratio = max_width / image_width
            cv2.resizeWindow(
                window_name,
                int(image_width * resize_ratio),
                int(image_height * resize_ratio),
            )
        cv2.imshow(window_name, display_image)
        print("Đang hiển thị ảnh. Nhấn phím bất kỳ trên cửa sổ để đóng.")
        cv2.waitKey(0)
    except cv2.error as error:
        print(f"Không thể mở cửa sổ OpenCV: {error}")
        print(f"Ảnh vẫn được lưu tại: {OUTPUT_PATH}")
    finally:
        try:
            cv2.destroyWindow(window_name)
        except cv2.error:
            pass
    return result


if __name__ == "__main__":
    main()
