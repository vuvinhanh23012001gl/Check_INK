import cv2
from app.config import YoloSegmentConfig
from app.engines.model_AI import ModelYoloSegment
from app.engines.AI_model_process import FrameModelYoloSegment
from app.judger.structure import SemiPermeableMembrane


def test_semi_permeable_membrane_judment() -> None:
    """Test phát hiện và so sánh border/inner membrane.
    Args:
        None.
    Returns:
        None.
    """
    config_inner = YoloSegmentConfig(
        path_model=r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\model\yolo\inner_permeable_membrane.pt",
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )

    config_border = YoloSegmentConfig(
        path_model=r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\model\yolo\border_permeable_membrane.pt",
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )
    

    print("=" * 60)
    print("Khởi tạo Model")
    print("=" * 60)
    config_inner = YoloSegmentConfig(
        path_model=r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\model\yolo\inner_permeable_membrane.pt",
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )

    config_border = YoloSegmentConfig(
        path_model=r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\model\yolo\border_permeable_membrane.pt",
        device="cpu",
        image_size=640,
        confidence=0.5,
        iou=0.5,
    )
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

    image = cv2.imread(
          r"C:\Users\anhuv\Desktop\train\img_input\image_aug0.jpg"
    )
    assert image is not None, "Không đọc được ảnh."
    status,data,img = judment.define(
        image,
        x1=0,
        y1=0,
        x2=80,
        y2=90
    )
   


if __name__ == "__main__":
    test_semi_permeable_membrane_judment()
# python -m app.tests.test_judment.test_semi_permeable_membrane_judment 
    # judment.judment_semi_permeable_membrane(
    #     image,
    #     x1=0,
    #     y1=0,
    #     x2=image.shape[1],
    #     y2=image.shape[0]
    # )

