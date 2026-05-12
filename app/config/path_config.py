from pathlib import Path

# Thư mục gốc
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_STORAGE = "storage"

# Tạo một biến gốc cho storage để các biến sau nối đuôi vào
BASE_PATH_STORAGE = BASE_DIR / PATH_STORAGE

# --- ĐỊNH NGHĨA THỦ CÔNG CÁC ĐƯỜNG DẪN ---
# 1. Các Folder (Đường dẫn tuyệt đối)
PATH_PRODUCT_IMG = str(BASE_PATH_STORAGE / "manager_product_images")
PATH_PRODUCT_ROI_PRODUCT_IMG = str(BASE_PATH_STORAGE / "manager_product_roi_images")

# 2. Các File (Đường dẫn tuyệt đối)
PATH_PRODUCT_DATA = str(BASE_PATH_STORAGE / "products_data.json")
PATH_PRODUCT_CHOOSE_PRODUCT = str(BASE_PATH_STORAGE / "choose_product_select.json")
PATH_PRODUCT_MODEL = str(BASE_PATH_STORAGE / "unetpp.pth")
PATH_FEATUERES_CFG_CAM = str(BASE_PATH_STORAGE / "features.cfg")
PATH_INFORMATION_SOFTWARE = str(BASE_PATH_STORAGE / "information_software.json")
PATH_CONFIG_SOFTWARE = str(BASE_PATH_STORAGE / "config_software.json")
PATH_CONFIG_CALIBRATION = str(BASE_PATH_STORAGE / "config_calibration.json")

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN TƯƠNG ĐỐI (Dùng cho Frontend hoặc lưu JSON) ---
PATH_CONFIG_POINTS =   str(BASE_PATH_STORAGE / "points.json")
# print(PATH_CONFIG_POINTS)
PATH_FOLDER_MODEL_DETECT_PATCH_CORE = str(BASE_PATH_STORAGE/"model"/"patch_core")


