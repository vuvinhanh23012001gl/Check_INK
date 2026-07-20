from app.engines.model_AI import ModelYoloObject
from app.engines.AI_model_process import FrameModelYoloObject
from app.engines.service import StructureFrameYoloService
from app.config import (
    YoloDetectObjectConfig,
    ClassNameObjectStructureDetectConfig,
    PATH_FILE_MODEL_YOLO_STRUCTURE,
)
import cv2


def main():
    config = YoloDetectObjectConfig(
        path_model=PATH_FILE_MODEL_YOLO_STRUCTURE,
        device="cpu",
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )

    print("Loading model...")
    model = ModelYoloObject(config)
    model.load_model()

    print("Warmup...")
    model.warmup()

    image = cv2.imread(
        r"C:\Users\anhuv\Desktop\train\yolo_co_lo_hay_khong_co_lo\date_3_7_40img\img\0.jpg"
    )

    if image is None:
        raise FileNotFoundError("Cannot read image.")

    frame_model = FrameModelYoloObject(model)
    service = StructureFrameYoloService(frame_model)

    result = service.get_objects_by_label(
        image=image,
        x1=300,
        y1=300,
        x2=image.shape[1],
        y2=image.shape[0],
        label=ClassNameObjectStructureDetectConfig.SENSOR_ARM.value,
    )
    print(result)
    if result.ok:
        print("Box Object:")
        print(result.data)
    else:
        print(result.message())
        print(result.error)


if __name__ == "__main__":
    main()

# python -m app.tests.engineer_sevice.test_structure_frame_yolo_service