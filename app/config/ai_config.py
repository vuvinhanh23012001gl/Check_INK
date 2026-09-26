from dataclasses import dataclass
from enum import StrEnum
import torch
from app.config.path_config import PATH_FILE_DEFAULT_PATCHCORE_INDEX




# Unet
@dataclass
class UnetConfig:
    path:str = None
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



@dataclass(slots=True)
class YoloSegmentConfig:
    """Cấu hình cho mô hình YOLO Segment."""
    path_model: str 
    device: str = "cpu"
    image_size: int = 640
    confidence: float = 0.25
    iou: float = 0.45


@dataclass(slots=True)
class YoloDetectObjectConfig:
    """Cấu hình cho mô hình YOLO Segment."""
    path_model: str 
    device: str = "cpu"
    image_size: int = 640
    confidence: float = 0.25
    iou: float = 0.45

# Không cho phép sửa lớp
class ClassNameObjectStructureDetectConfig(StrEnum):
    HOLE = "hole"
    COVER_ARM = "cover_arm"
    SENSOR_ARM = "sensor_arm"
  

@dataclass()
class ClassNameModelSurfaceConfig(StrEnum):
    AIR_BUBBLE = "air_bubble"
    SCRATCH = "scratch"

@dataclass(slots=True)
class PatchCoreAnomalyConfig:
    index_path: str = PATH_FILE_DEFAULT_PATCHCORE_INDEX
    nprobe: int = 10
    img_size: int = 256
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    overlay_alpha: float = 0.6  # Tỷ lệ ảnh gốc khi blend heatmap