from dataclasses import dataclass
from .path_config import PATH_FILE_UNET_DETECT


@dataclass
class UnetConfig:
    path:str = PATH_FILE_UNET_DETECT
    threshold: float = 0.5
    encoder: str = "resnet34"
    encoder_weights :str ="imagenet"
    type_model:str="detect_egde"
    in_channels:int= 3
    classes:int= 1
    activation= None
    img_size: int = 512
    kernel: int = 7
    min_area: int = 1000
    epsilon_ratio: float = 0.00007   # Tỷ lệ dọc đứng nhiều điểm trên polygon 

