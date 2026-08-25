from app.engines.model_AI import ModelYoloObject,ModelUnet,ModelPatchCore
from app.engines.AI_model_process import FrameModelYoloObject
from app.judger import WeldSeamAirBubbles
from app.config import PatchCoreAnomalyConfig
from app.engines.model_AI import ModelPatchCore
from app.config import (UnetConfig)
from app.engines.model_AI import ModelUnet
import cv2
from app.utils import Tool_OpenCv2



from app.engines.model_AI import ModelYoloObject
from app.engines.AI_model_process import FrameModelYoloObject
from app.config import YoloDetectObjectConfig,ClassNameObjectTargerDetectConfig


raw_im3232g = cv2.imread(r"C:\Users\anhuv\Desktop\train\patch_core_bot_khi\botkhi\img1\23 - Copy (17) - Copy - Copy_PatchCoreV1_20260707_102429_0.jpg"
)

config = YoloDetectObjectConfig(
        path_model=r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\model_air_bubble\train16\weights\best.pt",      
        device="cpu",                   # Hoặc "cpu"
        image_size=640,
        confidence=0.25,
        iou=0.45,
)
bubble = ModelYoloObject(config)
bubble.load_model()
bubble.warmup()

model_bubble =  FrameModelYoloObject(bubble)




obj_unet_config = UnetConfig()
obj_unet = ModelUnet(obj_unet_config)
def main():
    config = PatchCoreAnomalyConfig(
        index_path= r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\model_patch_core\patchcore_ivf.index",
        nprobe=10,
        img_size=256
    )
    # 2. Khởi tạo đối tượng Model
    model = ModelPatchCore(config=config)
    # 3. Load model và chạy warmup (Thực hiện khi khởi động API / Ứng dụng)
    model.load_model()
    model.warmup()
    # 4. Đọc ảnh đầu vào thực tế (Ví dụ từ camera hoặc file)
    raw_img = cv2.imread(r"C:\Users\anhuv\Desktop\train\patch_core_bot_khi\botkhi\img\1.jpg")
    if raw_img is not None:

        bounding_boxes = model.get_bounding_boxes(raw_img)
        output_image = model.draw_bounding_boxes(
            image=output_image, 
            boxes=bounding_boxes,color=(0,0,255)
        )
        Tool_OpenCv2.show_img(output_image)
        obj_weld_bubble_air =  WeldSeamAirBubbles(model_bubble)
        print("bounding_boxes",bounding_boxes)
        status, messages, output = obj_weld_bubble_air.define(
            raw_img,
            bounding_boxes
        )
        print("================ RESULT WELD AIR BUBBLE ================")
        print("PASS:", status)
        print("MESSAGE:")
        for msg in messages:
            print(msg)
        Tool_OpenCv2.show_img(output)






        # touching_boxes = obj_weld_bubble_air.get_touching_boundary_boxes(polygons,bounding_boxes)
        # Tool_OpenCv2.show_img(img)
        # Tool_OpenCv2.show_img(img_polygon)
        # img_touch = model.draw_bounding_boxes(raw_img,touching_boxes)
        # Tool_OpenCv2.show_img(img_touch)
        # print("polygons",polygons)
        # print("bounding_boxes",bounding_boxes)
        # print("touching_boxes",touching_boxes)

        
main()


    # if raw_img is not None:
    #     polygons = obj_unet.get_polygon(raw_img,UnetConfig.epsilon_ratio,UnetConfig.min_area)
    #     img_polygon = obj_unet.draw_polygon(raw_img,polygons)
    #     # Chuẩn hóa hệ màu về RGB trước khi truyền vào pipeline của Model PatchCore
    #     rgb_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
    #     img, bounding_boxes = model.get_bounding_boxes(rgb_img)
    #     obj_weld_bubble_air =  WeldSeamAirBubbles()
    #     touching_boxes = obj_weld_bubble_air.get_touching_boundary_boxes(polygons,bounding_boxes)
    #     img_touch  = obj_unet.draw_polygon(raw_img,touching_boxes)
    #     Tool_OpenCv2.show_img(img)
    #     Tool_OpenCv2.show_img(img_polygon)
    #     print("polygons",polygons)
    #     print("bounding_boxes",bounding_boxes)
    #     print("touching_boxes",touching_boxes)
    #     print("img_touch",img_touch)

# python -m app.tests.test_weld_seam_air_bubbles_detector

