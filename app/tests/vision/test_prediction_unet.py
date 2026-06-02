import cv2
from app.engines.unet_plus  import InferenceUnet, PredictionUnet
from app.config import UnetConfig
def main():

    config = UnetConfig()
    infer_unet = InferenceUnet(config)
    prediction = PredictionUnet(infer_unet)

    img = cv2.imread(r"C:\Users\anhuv\Desktop\train\img_input\1.jpg")

    if img is None:
        raise ValueError("Không đọc được ảnh")
    prediction.run(img)



if __name__ == "__main__":
    main()

    # python -m app.tests.vision.test_prediction_unet