from app.engines.model_AI import ModelYoloObject
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import YoloDetectObjectConfig,ClassNameObjectStructureDetectConfig
from app.utils import Tool_OpenCv2
import cv2
from app.config import (
    PATH_FILE_MODEL_YOLO_STRUCTURE,
)
def main():
    config = YoloDetectObjectConfig(
        path_model=PATH_FILE_MODEL_YOLO_STRUCTURE,      # Đường dẫn model
        device="cpu",                   # Hoặc "cpu"
        image_size=640,
        confidence=0.25,
        iou=0.45,
    )
    model = ModelYoloObject(config)
    print("Loading model...")
    model.load_model()
    print("Warmup...")
    model.warmup()
    image = cv2.imread(r"C:\Users\anhuv\Desktop\train\yolo_co_lo_hay_khong_co_lo\date_3_7_40img\img\3.jpg")
    if image is None:
        raise FileNotFoundError("Cannot read image: C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\tests\model_AI\img_test_object_detect_1.jpg")
    obj_targer = FrameModelYoloObject(model)
    # arr_obj = obj_targer.get_objects(image,0,0,image.shape[1],image.shape[0])
    status , coordinates ,img,_ = obj_targer.search(image,30,30,image.shape[1],image.shape[0],ClassNameObjectStructureDetectConfig.SENSOR_ARM.value)
    Tool_OpenCv2.show_img(img)
    print("status , coordinates",status , coordinates)
    
if __name__ == "__main__":
    main()
#python -m app.tests.engines.AI_model_process.test_frame_yolo_object_process

