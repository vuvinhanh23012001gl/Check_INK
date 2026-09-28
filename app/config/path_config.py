from pathlib import Path

# Thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
PATH_STORAGE = "storage"
PATH_INPUT = "input"
# Tao Patch input
BASE_PATH_INPUT_STORAGE = BASE_DIR / PATH_INPUT
# Tạo một biến gốc cho storage để các biến sau nối đuôi vào
BASE_PATH_STORAGE = BASE_DIR / PATH_STORAGE
PATH_FOLDER_STATIC = BASE_DIR / "static"
PATH_FOLDER_TEMPLATES = BASE_DIR / "templates"
URL_PATH_STATIC = "/static"
URL_PATH_STORAGE = "/storage"
URL_PATH_OUTPUT = "/output"

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
PATH_COUNT_PRODUCT = str(BASE_PATH_STORAGE / "count_product.json")

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN TƯƠNG ĐỐI (Dùng cho Frontend hoặc lưu JSON) ---
PATH_CONFIG_POINTS =   str(BASE_PATH_STORAGE / "points.json")
# print(PATH_CONFIG_POINTS)

PATH_FOLDER_IMG_COORDINATE_PRODUCT = str(BASE_PATH_STORAGE/"img_points")
BASE_PATH_OUTPUT = BASE_DIR / "output"
PATH_FOLDER_OUTPUT = BASE_PATH_OUTPUT
PATH_FOLDER_OUTPUT_JUDGMENT = PATH_FOLDER_OUTPUT / "judgment"
PATH_FOLDER_OUTPUT_RETRAIN = PATH_FOLDER_OUTPUT / "retrain"
PATH_DEFAULT_LOG_DISK = Path("C:/")
PATH_FOLDER_IMG_COORDINATE_OUTPUT = str(BASE_PATH_OUTPUT / "patch_core")
# Alias giữ tương thích với các module/test đang dùng tên cũ.
PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN = PATH_FOLDER_IMG_COORDINATE_OUTPUT
# file config
PATH_FILE_DATA_CONFIG_IAI = str(BASE_PATH_STORAGE/"config"/"iai.json")
PATH_FILE_DATA_CONFIG_COM = str(BASE_PATH_STORAGE/"config"/"COM.json")
PATH_FILE_DATA_CONFIG_JUDMENT_LAW = str(BASE_PATH_STORAGE/"config_judgment_law.json")

#Path File Unet
PATH_FILE_UNET_DETECT_WELD_LINE = str(BASE_PATH_INPUT_STORAGE/"model"/"unet"/"detect_weld_line.pth")
PATH_FILE_UNET_DETECT_FILM_BORDER_LINE = str(BASE_PATH_INPUT_STORAGE/"model"/"unet"/"detect_film_border_line.pth")
PATH_FOLDER_MODEL_DETECT_PATCH_CORE = str(BASE_PATH_INPUT_STORAGE/"model"/"patch_core")
PATH_FILE_DEFAULT_PATCHCORE_INDEX = str(WORKSPACE_DIR / "model" / "patchcore_ivf.index")
PATCHCORE_RUNTIME_DIR_NAME = "runtime"
PATCHCORE_INITIAL_DIR_NAME = "the_first"
PATCHCORE_INDEX_FILE_NAME = "patchcore.index"
PATH_FILE_END_CHIPPING_PATCHCORE_TRAIN_MANIFEST = str(
	BASE_PATH_STORAGE / "end_chipping_crop_patch_core_record.json"
)
PATH_FILE_FOREIGN_PATCHCORE_TRAIN_MANIFEST = str(
	BASE_PATH_STORAGE / "foreign_crop_patch_core_record.json"
)
PATH_FILE_MODEL_YOLO_STRUCTURE = str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"object_structure_detect.pt")
PATH_FILE_MODEL_YOLO_SURFACE  =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"object_surface_detect.pt")
PATH_FILE_MODEL_YOLO_FOREIGN_OBJECT = str(BASE_PATH_INPUT_STORAGE / "model" / "yolo" / "object_foreign object.pt")
PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_INER =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"segment_inner_permeable_membrane.pt")
PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_BORDER =  str(BASE_PATH_INPUT_STORAGE/"model"/"yolo"/"segment_border_permeable_membrane.pt")

# 3. Đường dẫn tài liệu hướng dẫn sử dụng (PDF)
PATH_DOCUMENTS_DIR = BASE_DIR / "static" / "docurments"
PATH_DOC_INSTRUCT_WORKER = str(PATH_DOCUMENTS_DIR / "instruct_worker.pdf")
PATH_DOC_INSTRUCT_STAFF_EE = str(PATH_DOCUMENTS_DIR / "instruct_staff_ee.pdf")
PATH_DOC_INSTRUCT_FIX_ERRO = str(PATH_DOCUMENTS_DIR / "instruct_fix_erro.pdf")


