from app.engines.model_AI import ModelYoloObject
from app.engines.AI_model_process import FrameModelYoloObject
from app.engines.service import SurfaceFrameYoloService

from app.config import (
    YoloDetectObjectConfig,
    ClassNameModelSurfaceConfig,
    PATH_FILE_MODEL_YOLO_SURFACE,
)

import cv2


def main():
    config = YoloDetectObjectConfig(
        path_model=PATH_FILE_MODEL_YOLO_SURFACE,
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
        r"C:\Users\anhuv\Desktop\train\patch_core_bot_khi\botkhi\bot_khi_and_xuoc\data_all\img1\1 - Copy.jpg"
    )

    if image is None:
        raise FileNotFoundError("Cannot read image.")

    frame_model = FrameModelYoloObject(model)
    service = SurfaceFrameYoloService(frame_model)

    result = service.get_objects_by_label(
        image=image,
        x1=0,
        y1=0,
        x2=image.shape[1],
        y2=image.shape[0],
        label=ClassNameModelSurfaceConfig.SCRATCH.value,
        width_canvas=1024,
    )

    print("=" * 60)

    if result.ok:
        print("Detect Success")
        print(f"Number of objects: {len(result.data)}")

        for index, obj in enumerate(result.data, start=1):
            print(f"\nObject {index}")
            print(f"Class      : {obj['class_name']}")
            print(f"Confidence : {obj['confidence']:.3f}")
            print(f"Touch X    : {obj['touch_x']}")
            print(f"Touch Y    : {obj['touch_y']}")
            print(f"BBox       : {obj['bbox']}")

        image_draw = frame_model.draw(image, result.data)

        cv2.imshow("Surface Detection", image_draw)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        print("Detect Failed")
        print(result.message())
        print(result.error)


if __name__ == "__main__":
    main()

# python -m app.tests.engines.service.test_surface_frame_yolo_service
# air_bubble