import time
import cv2

def test_automate_sampling_for_checking(deployment):
    img = cv2.imread(
        r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\app\storage\img_points\1\0\4.jpg"
    )

    if img is None:
        raise ValueError("Không đọc được ảnh.")

    print(f"Image size: {img.shape[1]} x {img.shape[0]}")

    start = time.perf_counter()

    lines, (width, height) = deployment.automate_sampling_for_checking(img,100,10)

    elapsed = time.perf_counter() - start

    print("\n========== RESULT ==========")
    print(f"Image size : {width} x {height}")
    print(f"Num lines  : {len(lines)}")
    print(f"Time       : {elapsed:.3f} s")

    return lines

from app.config import (
    UnetCofigAutoDetectLineMaster,
    UnetConfig,
)
from app.engines.unet_plus import DeploymentUnetUnet, InferenceUnet
obj_unet_config_line_master = UnetCofigAutoDetectLineMaster()
obj_unet_config = UnetConfig()
obj_infer_unet = InferenceUnet(obj_unet_config)
obj_deployment_Unet = DeploymentUnetUnet(
            obj_unet_config_line_master,
            obj_infer_unet
        )

deployment = DeploymentUnetUnet(
            obj_unet_config_line_master,
            obj_infer_unet
        )

test_automate_sampling_for_checking(deployment)
#  python -m app.tests.AI.test_unet_deloyment 