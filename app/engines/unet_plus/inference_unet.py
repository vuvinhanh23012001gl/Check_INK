from app.model import BaseAI
from app.config import UnetConfig
from app.utils import Folder
import segmentation_models_pytorch as smp
import torch
import gc
import  numpy as np 
import os
import cv2



class InferenceUnet(BaseAI):
    def __init__(self,config:UnetConfig = None):
        self.config = config
        self.device =  None
        self.model = None
        print("config.path",config.path)
        if not os.path.exists(config.path):
            Folder.create_file_path(config.path)
            raise ValueError("No_Model_Unet")
        self.load_model()
        self.warmup()
        

    def load_model(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = smp.UnetPlusPlus(
            encoder_name = self.config.encoder,
            encoder_weights = self.config.encoder_weights,
            in_channels = self.config.in_channels,
            classes = self.config.classes,
            activation= self.config.activation
        ).to(self.device)
        self.model.load_state_dict(torch.load(self.config.path, map_location = self.device))
        self.model.eval()
       
    
    def preprocess(self,image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (self.config.img_size, self.config.img_size))
        # cv2.imshow("Mask", image)  
        # cv2.waitKey(0)
        image = image.astype(np.float32) / 255.0  # chuyen tu anh 0-255 chuyen sang float de vao mo hinh
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image = (image - mean) / std
        image = np.transpose(image, (2, 0, 1))  #  (H, W, C) sang (C, H, W)
        image = np.expand_dims(image, axis=0)
        return torch.from_numpy(image).to(self.device)
    


    def predict(self,image):
        h, w = image.shape[:2]
        x = self.preprocess(image)
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.sigmoid(logits)
        print("Probs min/max:", probs.min().item(), probs.max().item())
        mask = (probs > self.config.threshold).to(torch.uint8)
        print("Mask unique:", torch.unique(mask))
        mask = mask.squeeze().cpu().numpy() * 255
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        mask = mask.astype(np.uint8)
        return mask
    

    def unload(self):
        if self.model is not None:
            try:
                self.model.to("cpu")
            except Exception:
                pass
            del self.model
            self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()
        print("Model unloaded")


    def warmup(self):
        print("Warmup: Running model with dummy image")
        dummy_image = np.zeros((224, 224, 3), dtype=np.uint8)  # Ảnh đen
        self.predict(dummy_image)
        print("RunOne Unet Compelete")



