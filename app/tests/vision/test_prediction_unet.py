import cv2

from app.engines.unet_plus import (
    InferenceUnet,
    DeploymentUnetUnet
)
from app.config import (
    UnetConfig,
    UnetCofigAutoDetectLineMaster
)

def main():

    unet_config = UnetConfig()
    auto_detect_config = UnetCofigAutoDetectLineMaster(
        distance_between_points_center_point=80
    )
    infer_unet = InferenceUnet(unet_config)
    prediction = DeploymentUnetUnet(
        auto_detect_config,
        infer_unet
    )
    img = cv2.imread(
        r"C:\Users\anhuv\Desktop\train\img_input\29.jpg"
    )
    if img is None:
        raise ValueError(
            "Không đọc được ảnh"
        )
    # prediction.automate_sampling_for_checking(
    #     img
    # )
    prediction.get_line_intersection_width(img,10,20,800,150)

if __name__ == "__main__":
    main()

    # python -m app.tests.vision.test_prediction_unet