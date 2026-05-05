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


ERROR_MESSAGE = {
    ErrorCode.CAMERA_TIMEOUT: "[Thất bại] Camera timeout",
    ErrorCode.CAMERA_DISCONNECT: "[Thất bại] Mất kết nối với camera",
    ErrorCode.CALIBRATION_TIMEOUT: "\n[Thất bại] Calibration timeout",
    ErrorCode.CALIBRATION_TIMEOUT_IMG_INPUT: "\n[Thất bại] Timeout khi chờ ảnh đầu vào calibration",
    ErrorCode.CALIBRATION_EMPTY_DATA: "\n[Thất bại] Không có dữ liệu pixel để tính toán calibration.",
    ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE: "\n[Thất bại] Số lượng mẫu đo không đủ để tính toán calibration.",
    ErrorCode.CALIBRATION_FILTERED_TOO_MUCH: "\n[Thất bại] Dữ liệu sau khi lọc nhiễu không đủ để tính toán calibration.",
    ErrorCode.CALIBRATION_MEDIAN_ZERO: "\n[Thất bại] Giá trị pixel trung vị bằng 0, không thể tính toán calibration.",
}