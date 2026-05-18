from enum import Enum

class ErrorCode(Enum):

    # ===== CAMERA =====
    CAMERA_TIMEOUT = 1001
    CAMERA_DISCONNECT = 1002

    # ===== VISION =====
    CALIBRATION_TIMEOUT = 2000
    CALIBRATION_TIMEOUT_IMG_INPUT = 2001
    CALIBRATION_EMPTY_DATA = 2002
    CALIBRATION_NOT_ENOUGH_SAMPLE = 2003
    CALIBRATION_FILTERED_TOO_MUCH = 2004
    CALIBRATION_MEDIAN_ZERO = 2005


    # products
   
    PRODUCT_ALREADY_EXISTED = 5001
    PRODUCT_NOT_FOUND = 5002
    PRODUCT_IMAGE_EMPTY = 5003
    PRODUCT_SAVE_IMAGE_FAIL = 5004

    # choose product
    DATA_INVALID = 5050

    # ===== POINT =====
    POINT_NOT_FOUND = 6001
    POINT_ALREADY_EXISTS = 6002
    IMAGE_INVALID = 6003


ERROR_MESSAGE = {
    ErrorCode.CAMERA_TIMEOUT: "[Thất bại] Camera timeout",
    ErrorCode.CAMERA_DISCONNECT: "[Thất bại] Mất kết nối với camera",
    ErrorCode.CALIBRATION_TIMEOUT: "\n[Thất bại] Calibration timeout",
    ErrorCode.CALIBRATION_TIMEOUT_IMG_INPUT: "\n[Thất bại] Timeout khi chờ ảnh đầu vào calibration",
    ErrorCode.CALIBRATION_EMPTY_DATA: "\n[Thất bại] Không có dữ liệu pixel để tính toán calibration.",
    ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE: "\n[Thất bại] Số lượng mẫu đo không đủ để tính toán calibration.",
    ErrorCode.CALIBRATION_FILTERED_TOO_MUCH: "\n[Thất bại] Dữ liệu sau khi lọc nhiễu không đủ để tính toán calibration.",
    ErrorCode.CALIBRATION_MEDIAN_ZERO: "\n[Thất bại] Giá trị pixel trung vị bằng 0, không thể tính toán calibration.",




    # products
    ErrorCode.PRODUCT_ALREADY_EXISTED:
        "[Cảnh báo] Sản phẩm hiện đã tồn tại. Hãy tạo sản phẩm mới mã ID khác",

    ErrorCode.PRODUCT_NOT_FOUND:
        "[Lỗi] Không tìm thấy product",

    ErrorCode.PRODUCT_IMAGE_EMPTY:
        "[Lỗi] Ảnh product rỗng",

    ErrorCode.PRODUCT_SAVE_IMAGE_FAIL:
        "[Lỗi] Không thể lưu ảnh product",


    # choose products
    ErrorCode.DATA_INVALID:
    "[Lỗi] Dữ liệu không hợp lệ",

    # ===== POINT =====
    ErrorCode.POINT_NOT_FOUND:
        "[Lỗi] Không tìm thấy point",
        
    ErrorCode.POINT_ALREADY_EXISTS :"\n[Thất bại] điểm đã tồn tại không được thêm điểm này",

    ErrorCode.IMAGE_INVALID:
        "[Lỗi] Ảnh đầu vào rỗng hoặc không hợp lệ",
} 
