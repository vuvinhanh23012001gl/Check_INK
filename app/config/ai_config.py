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
    epsilon_ratio: float = 0.0017   # Tỷ lệ dọc đứng nhiều điểm trên polygon 


@dataclass
class UnetCofigAutoDetectLineMaster:
    distance_between_points_center_point:int = 80 
    edge_point_spacing_polygons:int = 20
    intersection_detection_range:int = 300
    minimum_allowable_width:int = 5
    maximum_width_allowed:int = 300
    minimum_length_to_remove_line:int = 20
    length_extended_at_each_end:int = 20
    