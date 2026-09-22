import json
import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER,
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER,
    PATH_FILE_MODEL_YOLO_STRUCTURE,
    PATH_FILE_MODEL_YOLO_SURFACE,
    PATH_FILE_UNET_DETECT_FILM_BORDER_LINE,
    PATH_FILE_UNET_DETECT_WELD_LINE,
    YoloDetectObjectConfig,
    YoloSegmentConfig,
    UnetConfig,
)
from app.engines.AI_model_process import FrameModelYoloObject, FrameModelYoloSegment
from app.engines.model_AI import ModelUnet, ModelYoloObject, ModelYoloSegment
from app.engines.service import SurfaceFrameYoloService, StructureFrameYoloService
from app.judger import (
    ArmCoverDetector,
    ArmSensorDetector,
    BorderDetector,
    HoleDetector,
    Judment,
    MeasurementWeldingDetector,
    SemiPermeableMembrane,
    ScratchThePipeDetector,
    SlitDetector,
    WeldSeamAirBubbles,
)

CONFIG_PATH = PROJECT_ROOT / "app" / "storage" / "config_judgment_law.json"
IMAGE_PATH = PROJECT_ROOT / "app" / "storage" / "img_points" / "1" / "0" / "4.jpg"
OUTPUT_DIR = PROJECT_ROOT / "app" / "output" / "judgment_item_1_0_4"


def load_item_config() -> dict:
    """Đọc cấu hình judgment của product 1, frame 0, item 4.

    Input: Không có.
    Output: Cấu hình inspector của item 4.
    Errors: ``FileNotFoundError`` hoặc ``KeyError`` nếu thiếu file/dữ liệu.
    """
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as file:
        return json.load(file)["1"]["0"]["4"]


def create_registry() -> dict:
    """Khởi tạo registry detector bằng model thật trong workspace.

    Input: Các đường dẫn model từ ``app.config``.
    Output: Registry ánh xạ tên inspector với detector tương ứng.
    Errors: ``FileNotFoundError`` nếu thiếu model; lỗi model được thư viện AI
        phát sinh trong quá trình khởi tạo.
    """
    structure_frame = FrameModelYoloObject(
        ModelYoloObject(YoloDetectObjectConfig(path_model=PATH_FILE_MODEL_YOLO_STRUCTURE))
    )
    surface_frame = FrameModelYoloObject(
        ModelYoloObject(YoloDetectObjectConfig(path_model=PATH_FILE_MODEL_YOLO_SURFACE))
    )
    weld_model = ModelUnet(UnetConfig(path=PATH_FILE_UNET_DETECT_WELD_LINE))
    border_model = ModelUnet(UnetConfig(path=PATH_FILE_UNET_DETECT_FILM_BORDER_LINE))
    inner_membrane = FrameModelYoloSegment(
        ModelYoloSegment(
            YoloSegmentConfig(path_model=PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER)
        )
    )
    border_membrane = FrameModelYoloSegment(
        ModelYoloSegment(
            YoloSegmentConfig(path_model=PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER)
        )
    )

    return {
        "MeasurementWeldInspector": MeasurementWeldingDetector(weld_model),
        "SlitWeldInspector": SlitDetector(weld_model),
        "ArmSensorInspector": ArmSensorDetector(structure_frame),
        "ArmCoverInspector": ArmCoverDetector(structure_frame),
        "BorderFilmInspector": BorderDetector(border_model),
        "MembraneInspector": SemiPermeableMembrane(border_membrane, inner_membrane),
        "HoleItemInspector": HoleDetector(structure_frame),
        "ScratchedPipeItemInspector": ScratchThePipeDetector(surface_frame),
        "AirBubblesItemInspector": WeldSeamAirBubbles(surface_frame),
    }


def find_result_image(value):
    """Tìm ảnh NumPy được detector trả về trong một kết quả phán định.

    Input: Dữ liệu lồng nhau trong ``JudgmentResult.to_dict()``.
    Output: Ảnh NumPy đầu tiên tìm thấy hoặc ``None``.
    Errors: Không phát sinh.
    """
    if hasattr(value, "ndim") and hasattr(value, "shape"):
        if value.ndim == 2:
            return value
        if value.ndim == 3 and value.shape[2] in (1, 3, 4):
            return value
        return None
    if isinstance(value, dict):
        for child in value.values():
            result_image = find_result_image(child)
            if result_image is not None:
                return result_image
    elif isinstance(value, (list, tuple)):
        for child in value:
            result_image = find_result_image(child)
            if result_image is not None:
                return result_image
    return None


def summarize_result(value):
    """Rút gọn dữ liệu lớn để log kết quả từng inspector.

    Input: Dữ liệu kết quả có thể chứa ảnh NumPy và object lồng nhau.
    Output: Dữ liệu chỉ gồm giá trị có thể đọc trong console.
    Errors: Không phát sinh.
    """
    if hasattr(value, "shape") and hasattr(value, "dtype"):
        return f"<numpy image shape={value.shape} dtype={value.dtype}>"
    if isinstance(value, dict):
        return {key: summarize_result(child) for key, child in value.items()}
    if isinstance(value, list):
        return [summarize_result(child) for child in value]
    if isinstance(value, tuple):
        return tuple(summarize_result(child) for child in value)
    return value


def log_and_show_results(summary: dict, fallback_image) -> None:
    """In chi tiết và hiển thị ảnh sau khi toàn bộ inspector đã chạy.

    Input: Summary của Judment và ảnh gốc dùng làm fallback.
    Output: Không trả về; lưu ảnh kết quả vào output và hiển thị từng ảnh nếu
        môi trường Windows có hỗ trợ GUI OpenCV.
    Errors: Không dừng test nếu OpenCV không mở được cửa sổ.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("===== JUDMENT DETAIL LOG =====")
    print(f"Overall: {summary['status']} - {summary['message']}")
    for name, result in summary["inspectors"].items():
        print(f"\n--- {name} ---")
        print(f"status: {result.get('status')}")
        print(f"ok: {result.get('ok')}")
        print(f"message: {result.get('message')}")
        print(f"errors: {result.get('errors')}")
        print(f"runtime_data: {summarize_result(result.get('runtime_data'))}")
        print(f"comparison_data: {summarize_result(result.get('comparison_data'))}")
        result_image = find_result_image(result)
        if result_image is None:
            result_image = fallback_image
        output_path = OUTPUT_DIR / f"{name}.jpg"
        if not cv2.imwrite(str(output_path), result_image):
            raise AssertionError(f"Không lưu được ảnh kết quả: {output_path}")
        print(f"result_image: {output_path}")
        show_result_image(name, result_image)
    cv2.destroyAllWindows()


def show_result_image(name: str, image) -> None:
    """Hiển thị ảnh cho đến khi đóng cửa sổ rồi chuyển sang ảnh kế tiếp.

    Input: Tên cửa sổ và ảnh NumPy cần hiển thị.
    Output: Không trả về; kết thúc khi cửa sổ được đóng hoặc nhấn Esc/q.
    Errors: Không dừng test nếu môi trường không hỗ trợ OpenCV GUI.
    """
    try:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.imshow(name, image)
        while True:
            key = cv2.waitKey(50) & 0xFF
            if key in (27, ord("q")):
                break
            try:
                if cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except cv2.error:
                break
        cv2.destroyWindow(name)
        cv2.waitKey(1)
    except cv2.error as error:
        print(f"Không hiển thị được {name} bằng OpenCV GUI: {error}")


def main() -> dict:
    """Chạy toàn bộ inspector cấu hình item 1/0/4 trên ảnh runtime thật.
    Input: File config judgment, ảnh ``img_points/1/0/4.jpg`` và model thật.
    Output: Summary gồm trạng thái tổng và trạng thái từng tool.
    Errors: ``AssertionError`` nếu ảnh/config không hợp lệ hoặc thiếu detector.
    """
    image = cv2.imread(str(IMAGE_PATH))
    if image is None:
        raise AssertionError(f"Không đọc được ảnh test: {IMAGE_PATH}")
    config = load_item_config()
    registry = create_registry()
    supported_config = {
        name: inspector_config
        for name, inspector_config in config.items()
        if name in registry
    }
    skipped = sorted(set(config) - set(supported_config))
    if skipped:
        print(f"Bỏ qua inspector chưa có detector Python: {skipped}")

    summary = Judment(registry).run_summary(image, supported_config)
    assert set(summary["inspectors"]) == set(supported_config)
    assert summary["status"] in {"OK", "NG"}
    log_and_show_results(summary, image)
    print("\nJudment config item 1/0/4 runtime test: PASS")
    return summary


if __name__ == "__main__":
    main()
