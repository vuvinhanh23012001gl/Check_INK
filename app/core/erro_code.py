from enum import Enum


class ErrorCode(Enum):

    # =====================================
    # CAMERA
    # =====================================

    CAMERA_TIMEOUT = 1001
    CAMERA_DISCONNECT = 1002

    # =====================================
    # CALIBRATION
    # =====================================
    CALIBRATION_ALREADY_EXISTS = 1500
    CALIBRATION_NOT_FOUND = 1501
    CALIBRATION_NOT_ENOUGH_SAMPLE = 1502
    CALIBRATION_EMPTY_DATA  = 1503
    CALIBRATION_INVALID_REAL_LENGTH = 1504
    CALIBRATION_INVALID_MEAN = 1505
    CALIBRATION_FILTERED_TOO_MUCH = 1506
    # =====================================
    # PRODUCT
    # =====================================

    PRODUCT_ALREADY_EXISTED = 5001
    PRODUCT_NOT_FOUND = 5002
    PRODUCT_IMAGE_EMPTY = 5003
    PRODUCT_SAVE_IMAGE_FAIL = 5004

    PRODUCT_ID_INVALID = 5005

    # =====================================
    # DATA
    # =====================================

    DATA_INVALID = 5050
    INVALID_INPUT = 5051
    # =====================================
    # FRAME
    # =====================================

    FRAME_ID_INVALID = 5500

    # =====================================
    # POINT
    # =====================================

    POINT_NOT_FOUND = 6001
    POINT_ALREADY_EXISTS = 6002
    IMAGE_INVALID = 6003

    FRAME_NOT_FOUND = 6050

    POINT_X_INVALID = 6004
    POINT_Y_INVALID = 6005
    POINT_Z_INVALID = 6006

    
ERROR_MESSAGE = {

    # =====================================
    # CAMERA
    # =====================================

    ErrorCode.CAMERA_TIMEOUT:
        "[Thất bại] Camera timeout",

    ErrorCode.CAMERA_DISCONNECT:
        "[Thất bại] Mất kết nối với camera",

    # =====================================
    # CALIBRATION
    # =====================================


    ErrorCode.CALIBRATION_ALREADY_EXISTS :"[Cảnh báo] Calibartion đã tồn tại",
    ErrorCode.CALIBRATION_NOT_FOUND :"[Cảnh báo] Không tìm thấy Calibration",
    ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE: "[Cảnh báo] Không đủ dữ liệu hiệu chuẩn",
    ErrorCode.CALIBRATION_EMPTY_DATA: "[Cảnh báo] Dữ liệu hiệu chuẩn rỗng",
    ErrorCode.CALIBRATION_INVALID_REAL_LENGTH: "[Cảnh báo] Chiều dài thực không hợp lệ",
    ErrorCode.CALIBRATION_INVALID_MEAN: "[Lỗi] Giá trị trung bình pixel không hợp lệ (= 0)",
    ErrorCode.CALIBRATION_FILTERED_TOO_MUCH: "[Cảnh báo] Lọc nhiễu quá nhiều, không đủ dữ liệu tin cậy",
   
    # =====================================
    # PRODUCT
    # =====================================

    ErrorCode.PRODUCT_ALREADY_EXISTED:
        "[Cảnh báo] Sản phẩm hiện đã tồn tại. Hãy tạo sản phẩm mới mã ID khác",

    ErrorCode.PRODUCT_NOT_FOUND:
        "[Lỗi] Không tìm thấy product",

    ErrorCode.PRODUCT_IMAGE_EMPTY:
        "[Lỗi] Ảnh product rỗng",

    ErrorCode.PRODUCT_SAVE_IMAGE_FAIL:
        "[Lỗi] Không thể lưu ảnh product",

    ErrorCode.PRODUCT_ID_INVALID:
        "[Lỗi] product_id không hợp lệ",

    # =====================================
    # DATA
    # =====================================

    ErrorCode.DATA_INVALID:
        "[Lỗi] Dữ liệu không hợp lệ",

    # =====================================
    # FRAME
    # =====================================

    ErrorCode.FRAME_ID_INVALID:
        "[Lỗi] frame_id không hợp lệ",

    # =====================================
    # POINT
    # =====================================

    ErrorCode.POINT_NOT_FOUND:
        "[Lỗi] Không tìm thấy point",

    ErrorCode.POINT_ALREADY_EXISTS:
        "[Thất bại] Point đã tồn tại",

    ErrorCode.IMAGE_INVALID:
        "[Lỗi] Ảnh đầu vào rỗng hoặc không hợp lệ",

    ErrorCode.POINT_X_INVALID:
        "[Lỗi] point.x không hợp lệ",

    ErrorCode.POINT_Y_INVALID:
        "[Lỗi] point.y không hợp lệ",

    ErrorCode.POINT_Z_INVALID:
        "[Lỗi] point.z không hợp lệ",

    ErrorCode.INVALID_INPUT:
    "[Lỗi] Dữ liệu đầu vào không hợp lệ",

    ErrorCode.FRAME_NOT_FOUND:
    "[Lỗi] Frame này đang không tồn tại",
}

# print(" ErrorCode.POINT_ALREADY_EXISTS", ErrorCode.POINT_ALREADY_EXISTS.name)
# print(" ErrorCode.POINT_ALREADY_EXISTS", ErrorCode.POINT_ALREADY_EXISTS.value)