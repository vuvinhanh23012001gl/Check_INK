import sys
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER,
    PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER,
    YoloSegmentConfig,
)
from app.engines.model_AI import ModelYoloSegment
from app.engines.AI_model_process import FrameModelYoloSegment
from app.judger import SemiPermeableMembrane


def test_semi_permeable_membrane_judment() -> None:
    """Test phát hiện và so sánh border/inner membrane.
    Args:
        None.
    Returns:
        None.
    """
    config_inner = YoloSegmentConfig(
        path_model=PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER,
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )

    config_border = YoloSegmentConfig(
        path_model=PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER,
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )
    

    print("=" * 60)
    print("Khởi tạo Model")
    print("=" * 60)
    model_inner = ModelYoloSegment(config_inner)  # tien hanh load model luon
    model_border = ModelYoloSegment(config_border)  # tien hanh load model luon
    print("Model loaded.\n")
    print("=" * 60)
    print("Khởi tạo Service")
    print("=" * 60)
    service_inner = FrameModelYoloSegment(model_inner)
    service_border = FrameModelYoloSegment(model_border)
    judment = SemiPermeableMembrane(
        service_border,
        service_inner
    )

    image_path = r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\img_points\1\1\1.jpg"
    image = cv2.imread(str(image_path))
    assert image is not None, "Không đọc được ảnh."
    status,data,img = judment.define(
        image,
        x1=0,
        y1=0,
        x2=image.shape[1],
        y2=image.shape[0]
    )
    comparison = judment.compare(True, (status, data, img))
    result = judment.judge(comparison)
    print("status:", status)
    print("intersection_points:", data)
    print("judgment:", result.to_dict())
    assert result.status in {"OK", "NG"}
   


if __name__ == "__main__":
    test_semi_permeable_membrane_judment()
# python -m app.tests.test_semi_permeable_membrane_judment
    # judment.judment_semi_permeable_membrane(
    #     image,
    #     x1=0,
    #     y1=0,
    #     x2=image.shape[1],
    #     y2=image.shape[0]
    # )

