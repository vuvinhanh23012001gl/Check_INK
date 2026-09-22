import json
import sys
from pathlib import Path
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PATH_FILE_UNET_DETECT_WELD_LINE, UnetConfig
from app.engines.model_AI import ModelUnet
from app.judger import MeasurementWeldingDetector


PRODUCT_ID = "1"
FRAME_ID = "0"
ITEM_ID = "0"
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / PRODUCT_ID / FRAME_ID / f"{ITEM_ID}.jpg"
JUDGMENT_PATH = PROJECT_ROOT / "app" / "storage" / "config_judgment_law.json"
CALIBRATION_PATH = PROJECT_ROOT / "app" / "storage" / "config_calibration.json"
OUTPUT_PATH = PROJECT_ROOT / "app" / "output" / "measurement_welding_runtime.jpg"
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 768


def load_json(path: Path) -> dict:
    """Đọc một file JSON UTF-8.

    Input: ``path`` là đường dẫn file JSON.
    Output: dictionary nội dung file.
    Errors: ``FileNotFoundError`` nếu thiếu file; lỗi JSON nếu nội dung sai.
    """
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {path}")
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def convert_lines_to_image(standard_data: dict, image: np.ndarray) -> list[tuple[float, ...]]:
    """Quy đổi các line chuẩn từ tọa độ canvas sang tọa độ ảnh runtime.

    Input: cấu hình ``MeasurementWeldInspector`` và ảnh runtime.
    Output: danh sách line ``(x1, y1, x2, y2)`` theo pixel ảnh.
    Errors: ``ValueError`` nếu cấu hình line thiếu tọa độ.
    """
    scale_x = image.shape[1] / CANVAS_WIDTH
    scale_y = image.shape[0] / CANVAS_HEIGHT
    lines = []
    for line_id, line in sorted(standard_data.items(), key=lambda item: int(item[0])):
        try:
            lines.append((
                float(line["xStart"]) * scale_x,
                float(line["yStart"]) * scale_y,
                float(line["xEnd"]) * scale_x,
                float(line["yEnd"]) * scale_y,
            ))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Line {line_id} thiếu tọa độ hợp lệ") from error
    return lines


def draw_result(
    image: np.ndarray,
    runtime_data: dict,
    comparison_data: dict,
) -> np.ndarray:
    """Vẽ polygon, line đo, giao điểm, level và trạng thái lên ảnh.

    Input: ảnh gốc, output ``define`` và output ``compare``.
    Output: ảnh NumPy đã vẽ kết quả.
    Errors: không phát sinh; dữ liệu polygon/line rỗng sẽ được bỏ qua.
    """
    output = image.copy()
    polygon = runtime_data.get("polygon")
    if polygon is not None and len(polygon) >= 3:
        polygon_points = np.asarray(polygon).reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(output, [polygon_points], True, (255, 255, 0), 3)

    comparisons = {
        item["line_index"]: item for item in comparison_data["comparisons"]
    }
    for runtime_line in runtime_data["lines"]:
        line_index = runtime_line["line_index"]
        comparison = comparisons[line_index]
        original = runtime_line["original_line"]
        start = (int(round(original[0])), int(round(original[1])))
        end = (int(round(original[2])), int(round(original[3])))
        color = (0, 255, 0) if comparison["is_valid"] else (0, 0, 255)
        cv2.line(output, start, end, color, 2)

        point1 = runtime_line.get("intersection_point_1")
        point2 = runtime_line.get("intersection_point_2")
        if point1 is not None and point2 is not None:
            point1 = tuple(int(round(value)) for value in point1)
            point2 = tuple(int(round(value)) for value in point2)
            cv2.circle(output, point1, 7, (255, 0, 0), -1)
            cv2.circle(output, point2, 7, (255, 0, 0), -1)
            cv2.line(output, point1, point2, color, 4)

        distance = comparison["distance_mm"]
        distance_text = "N/A" if distance is None else f"{distance:.3f} mm"
        label = (
            f"Line {comparison['name_line']}: {comparison['level']} - "
            f"{'OK' if comparison['is_valid'] else 'NG'} - {distance_text}"
        )
        cv2.putText(
            output,
            label,
            (start[0], max(30, start[1] - 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )
    return output


def main():
    """Chạy MeasurementWeldingDetector với model, ảnh và JSON thật.

    Input: các hằng số product/frame/item và đường dẫn ở đầu file.
    Output: ``JudgmentResult``, log từng line và ảnh kết quả trong ``app/output``.
    Errors: lỗi file, ảnh, cấu hình, calibration hoặc model được báo trực tiếp.
    """
    print("===== RUNTIME MEASUREMENT WELDING =====")
    print(f"Product={PRODUCT_ID}, Frame={FRAME_ID}, Item={ITEM_ID}")
    print("Model:", PATH_FILE_UNET_DETECT_WELD_LINE)
    print("Ảnh:", IMAGE_PATH)

    if not Path(PATH_FILE_UNET_DETECT_WELD_LINE).exists():
        raise FileNotFoundError(f"Không tìm thấy model: {PATH_FILE_UNET_DETECT_WELD_LINE}")
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {IMAGE_PATH}")

    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise RuntimeError(f"OpenCV không đọc được ảnh: {IMAGE_PATH}")

    judgment_config = load_json(JUDGMENT_PATH)
    calibration_config = load_json(CALIBRATION_PATH)
    standard_data = judgment_config[PRODUCT_ID][FRAME_ID][ITEM_ID][
        "MeasurementWeldInspector"
    ]
    scale_mm_per_pixel = float(
        calibration_config[PRODUCT_ID][FRAME_ID]["result_parameters"][
            "scale_mm_per_pixel"
        ]
    )
    lines = convert_lines_to_image(standard_data, image)

    print("Kích thước ảnh:", image.shape)
    print("Scale mm/pixel:", scale_mm_per_pixel)
    print("Số line chuẩn:", len(lines))
    for line_id, line in enumerate(lines):
        print(f"  Line {line_id} tọa độ ảnh: {line}")

    print("\n[1] Load model UNet thật...")
    model_config = UnetConfig(path=str(PATH_FILE_UNET_DETECT_WELD_LINE))
    model = ModelUnet(model_config)
    detector = MeasurementWeldingDetector(model)

    print("[2] Define: chạy model và đo line...")
    runtime_data = detector.define(
        image,
        lines,
        Approx_value=model_config.epsilon_ratio,
        min_area=model_config.min_area,
    )

    print("[3] Compare: đổi pixel sang mm và xếp level...")
    comparison_data = detector.compare(
        {"MeasurementWeldInspector": standard_data},
        runtime_data,
        scale_mm_per_pixel=scale_mm_per_pixel,
    )

    print("[4] Judge: kết luận toàn bộ item...")
    result = detector.judge(comparison_data)
    for item in comparison_data["comparisons"]:
        print(
            f"  Line {item['name_line']}: "
            f"pixel={item['distance_pixel']}, mm={item['distance_mm']}, "
            f"level={item['level']}, status={'OK' if item['is_valid'] else 'NG'}"
        )
    print("Kết quả item:", result.status)
    print("Thông báo:", result.message)
    print("Lỗi:", result.errors)

    output = draw_result(image, runtime_data, comparison_data)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT_PATH), output):
        raise RuntimeError(f"Không lưu được ảnh kết quả: {OUTPUT_PATH}")
    print("Ảnh kết quả:", OUTPUT_PATH)
    return result


if __name__ == "__main__":
    main()
