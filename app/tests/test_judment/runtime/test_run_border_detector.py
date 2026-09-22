import sys
import json
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import UnetConfig
from app.engines.model_AI import ModelUnet
from app.judger import BorderDetector


MODEL_PATH = PROJECT_ROOT / "unet_test_model_vien" / "unetpp.pth"
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "1.jpg"
JUDGMENT_CONFIG_PATH = PROJECT_ROOT / "app" / "storage" / "config_judgment_law.json"
CALIBRATION_CONFIG_PATH = PROJECT_ROOT / "app" / "storage" / "config_calibration.json"

# Các line được lưu theo pixel canvas 1024 x 768.
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 768


def main():
    """Chạy BorderDetector với UNet và ảnh master thật.

    Input: MODEL_PATH, IMAGE_PATH và LINES ở đầu file.
    Output: In kết quả giao điểm, khoảng cách và phán định từng line.
    Errors: FileNotFoundError nếu thiếu model/ảnh; RuntimeError nếu ảnh hoặc
        polygon không hợp lệ.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy model UNet: {MODEL_PATH}")
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh master: {IMAGE_PATH}")

    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise RuntimeError(f"Không đọc được ảnh master: {IMAGE_PATH}")

    config = UnetConfig(path=MODEL_PATH)
    model = ModelUnet(config)
    detector = BorderDetector(model)

    if not JUDGMENT_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy cấu hình judgment: {JUDGMENT_CONFIG_PATH}")
    if not CALIBRATION_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy cấu hình calibration: {CALIBRATION_CONFIG_PATH}")

    with open(JUDGMENT_CONFIG_PATH, "r", encoding="utf-8-sig") as file:
        judgment_config = json.load(file)
    with open(CALIBRATION_CONFIG_PATH, "r", encoding="utf-8-sig") as file:
        calibration_config = json.load(file)

    standard_data = judgment_config["1"]["0"]["1"]["BorderFilmInspector"]
    scale_mm_per_pixel = float(
        calibration_config["1"]["0"]["result_parameters"]["scale_mm_per_pixel"]
    )
    image_lines = [
        (
            float(line["xStart"]),
            float(line["yStart"]),
            float(line["xEnd"]),
            float(line["yEnd"]),
        )
        for _, line in sorted(standard_data.items(), key=lambda item: int(item[0]))
    ]

    runtime_data = detector.define(image, image_lines)
    print("polygon vertices:", len(runtime_data["polygon"]) if runtime_data["polygon"] is not None else 0)
    for item in runtime_data["lines"]:
        print(
            f"line={item['line_index']}, valid={item['is_valid']}, "
            f"p1={item['intersection_point_1']}, "
            f"p2={item['intersection_point_2']}, "
            f"distance_image_pixel={item['distance_pixel']:.3f}, "
            f"distance_mm={item['distance_pixel'] * scale_mm_per_pixel:.3f}"
        )

    comparison_data = detector.compare(
        standard_data,
        runtime_data,
        scale_mm_per_pixel=scale_mm_per_pixel,
    )
    result = detector.judge(comparison_data)
    print(f"scale_mm_per_pixel: {scale_mm_per_pixel}")
    print("judgment status:", result.status)
    print("judgment message:", result.message)
    for item in comparison_data["comparisons"]:
        print(
            f"line={item['line_index']}, measured={item['distance_mm']:.3f} mm, "
            f"standard={item['width_min']:.3f}..{item['width_max']:.3f} mm, "
            f"status={'OK' if item['is_valid'] else 'NG'}"
        )

    display_image = image.copy()
    polygon = runtime_data["polygon"]
    if polygon is not None and len(polygon) >= 3:
        polygon_points = polygon.reshape((-1, 1, 2)).astype("int32")
        cv2.polylines(
            display_image,
            [polygon_points],
            isClosed=True,
            color=(0, 255, 0),
            thickness=3,
        )

    comparisons_by_index = {
        item["line_index"]: item for item in comparison_data["comparisons"]
    }
    for item in runtime_data["lines"]:
        line_index = item["line_index"]
        line = item["original_line"]
        line_start = (int(round(line[0])), int(round(line[1])))
        line_end = (int(round(line[2])), int(round(line[3])))
        comparison = comparisons_by_index.get(line_index, {})
        line_color = (0, 255, 0) if comparison.get("is_valid") else (0, 0, 255)
        cv2.line(display_image, line_start, line_end, line_color, 2)

        if item["is_valid"]:
            point_1 = tuple(int(round(value)) for value in item["intersection_point_1"])
            point_2 = tuple(int(round(value)) for value in item["intersection_point_2"])
            distance = item["distance_pixel"]
            distance_mm = comparison.get("distance_mm", distance * scale_mm_per_pixel)
            cv2.line(display_image, point_1, point_2, line_color, 4)
            cv2.circle(display_image, point_1, 8, (255, 0, 0), -1)
            cv2.circle(display_image, point_2, 8, (255, 0, 0), -1)
            label_position = (
                int((point_1[0] + point_2[0]) / 2),
                int((point_1[1] + point_2[1]) / 2) - 10,
            )
            label = (
                f"L{line_index}: {'OK' if comparison.get('is_valid') else 'NG'} "
                f"{distance_mm:.3f}mm ({distance:.1f}px)"
            )
            cv2.putText(
                display_image,
                label,
                label_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                line_color,
                2,
                cv2.LINE_AA,
            )
        else:
            label = f"L{line_index}: NG - INVALID"
            cv2.putText(
                display_image,
                label,
                line_start,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 165, 255),
                2,
                cv2.LINE_AA,
            )

    detector.show(display_image, window_name="Border Detector Result")
    return result


if __name__ == "__main__":
    main()
