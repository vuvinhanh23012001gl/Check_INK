from pathlib import Path

# Thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_STORAGE = "storage"
PATH_INPUT = "input"
# Tao Patch input
BASE_PATH_INPUT_STORAGE = BASE_DIR / PATH_INPUT
# Tạo một biến gốc cho storage để các biến sau nối đuôi vào
BASE_PATH_STORAGE = BASE_DIR / PATH_STORAGE

# --- ĐỊNH NGHĨA THỦ CÔNG CÁC ĐƯỜNG DẪN ---
# 1. Các Folder (Đường dẫn tuyệt đối)
PATH_PRODUCT_IMG = str(BASE_PATH_STORAGE / "manager_product_images")
PATH_PRODUCT_ROI_PRODUCT_IMG = str(BASE_PATH_STORAGE / "manager_product_roi_images")

# 2. Các File (Đường dẫn tuyệt đối)
PATH_PRODUCT_DATA = str(BASE_PATH_STORAGE / "products_data.json")
PATH_PRODUCT_CHOOSE_PRODUCT = str(BASE_PATH_STORAGE / "choose_product_select.json")
# PATH_PRODUCT_MODEL = str(BASE_PATH_STORAGE / "unetpp.pth")
PATH_FEATUERES_CFG_CAM = str(BASE_PATH_STORAGE / "features.cfg")
PATH_INFORMATION_SOFTWARE = str(BASE_PATH_STORAGE / "information_software.json")
PATH_CONFIG_SOFTWARE = str(BASE_PATH_STORAGE / "config_software.json")
PATH_CONFIG_CALIBRATION = str(BASE_PATH_STORAGE / "config_calibration.json")

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN TƯƠNG ĐỐI (Dùng cho Frontend hoặc lưu JSON) ---
PATH_CONFIG_POINTS =   str(BASE_PATH_STORAGE / "points.json")
# print(PATH_CONFIG_POINTS)

PATH_FOLDER_IMG_COORDINATE_PRODUCT = str(BASE_PATH_STORAGE/"img_points")
PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN = str(BASE_PATH_STORAGE/"retrain"/"patch_core")
# file config
PATH_FILE_DATA_CONFIG_IAI = str(BASE_PATH_STORAGE/"config"/"iai.json")
PATH_FILE_DATA_CONFIG_COM = str(BASE_PATH_STORAGE/"config"/"COM.json")
PATH_FILE_DATA_CONFIG_JUDMENT_LAW = str(BASE_PATH_STORAGE/"config_judgment_law.json")

#Path File Unet
PATH_FILE_UNET_DETECT_WELD_LINE = str(BASE_PATH_INPUT_STORAGE/"model"/"unet"/"detect_weld_line.pth")
PATH_FILE_UNET_DETECT_FILM_BORDER_LINE = str(BASE_PATH_INPUT_STORAGE/"model"/"unet"/"detect_film_border_line.pth")
PATH_FOLDER_MODEL_DETECT_PATCH_CORE = str(BASE_PATH_INPUT_STORAGE/"model"/"patch_core")
PATH_FILE_MODEL_YOLO_STRUCTURE = str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"object_structure_detect.pt")
PATH_FILE_MODEL_YOLO_SURFACE  =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"object_surface_detect.pt")
PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"segment_inner_permeable_membrane.pt")
PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"segment_border_permeable_membrane.pt")


