from app.repository import CalibrationReponsitory
from app.services import CalibrationService, PointService
from app.model import Calibration
from app.config import (
    PATH_CONFIG_POINTS,
    PATH_CONFIG_CALIBRATION,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
    BASE_DIR
)


from app.repository import PointRepository


# =========================================
# PRINT RESULT
# =========================================

def print_result(
    title,
    result
):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print("OK:", result.ok)
    print("DATA:", result.data)
    print("ERROR:", result.error)


# =========================================
# TEST
# =========================================

def test_calibration_service():

    # =========================================
    # INIT
    # =========================================

    point_repository = PointRepository(
        PATH_CONFIG_POINTS
    )

    point_service = PointService(
        point_repository,
        PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
        PATH_FOLDER_IMG_COORDINATE_PRODUCT,
        PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
        BASE_DIR
    )

    calibration_repository = CalibrationReponsitory(
        PATH_CONFIG_CALIBRATION
    )

    service = CalibrationService(
        point_service,
        calibration_repository
    )

    # # =========================================
    # # TEST PARAM
    # # =========================================

    product_id = 2
    frame_id = 1

    calibration_data = {
        f"{Calibration.CALCULATION_PARAMETER}": {
            "number_capture": 10000,
            "name_item": "",
            "id_tems": "",
            "startX": 0.0,
            "startY": 0.0,
            "endX": 0.0,
            "endY": 0.0,
            "reality_mm": 1110.0  # Đã chuyển sang nhóm này
        },
        f"{Calibration.RESULT_PARAMETER}": {
            "pixel_mean": 500.0,
            "pixel_std": 2.5,
            "cv": 0.0,
            "scale_mm_per_pixel": 0.0,
            "scale_error_mm_per_pixel": 0.0,
            "confidence": 0.0,
            "samples_used": 0,
            "samples_raw": 0,
            "mad": 0.0
        }
    }

    #obj_calibration = Calibration.from_dict(calibration_data)
    # # =========================================
    # # ADD
    # # =========================================

    # result = service.add_calibration(
    #     2,
    #     1,
    #     obj_calibration
    # )

    # print_result(
    #     "ADD CALIBRATION",
    #     result
    # )

    # # =========================================
    # # GET
    # # =========================================

    # result = service.get_calibration(1,0)
    # print(result)
    # if result.ok:
    #     calibration_dict = result.data.to_dict()   #  result.data. chinh la doi tuong
    #     print("calibration_dict",calibration_dict)
    #     res_params = calibration_dict.get(Calibration.RESULT_PARAMETER, {})
    #     print("\nReality mm:", res_params.get("reality_mm"))
    #     print("Pixel mean:", res_params.get("pixel_mean"))
    #     print("Pixel std:", res_params.get("pixel_std"))
    #     cv = res_params.get("cv", 0.0)
    #     print(f"CV %: {cv * 100:.2f}%")

    # # =========================================
    # # UPDATE
    # # =========================================

    # update_data = {
    #     "reality_mm": 300.0,
    #     "pixel_mean": 1000.0,
    #     "pixel_std": 1.0,
    #     "calibration_mm_per_pixel": 0.1,
    #     "number_capture": 20
    # }



    # # =========================================
    # # DELETE
    # # =========================================
    # result = service.delete_calibration(2, 0)

    # # In kết quả kiểm tra ra màn hình console
    # print_result(
    #     "DELETE CALIBRATION",
    #     result
    # )   

    # exists_before = service.is_calibration_exists(2,3)
    # print(f"Product {product_id}, Frame {frame_id} đã tồn tại?: {exists_before}")

    # test calculate_calibration_metrics
    
    # pixel_list = [500.2, 499.8, 500.5, 501.1, 498.9, 500.0, 500.3, 499.5, 500.0, 500.0]
    # reality_length = 100
    # calib_result = service.calculate_calibration_metrics(pixel_list, reality_length)
    # print(calib_result)
    # if calib_result.ok:
    #     print("Du lieu tra ve",calib_result.data)

    # # =========================================
    # # test  analyze_data_to_arrays
    # # =========================================
    # data = {
    #                 '1': {
    #                     '0': {
    #                         'calculation_parameters': {
    #                             'lineName': '1',
    #                             'realityMM': 11.0,
    #                             'captureCount': 111,
    #                             'xStart': 441,
    #                             'yStart': 139,
    #                             'xEnd': 420,
    #                             'yEnd': 318,
    #                             'coordinateX': 144,
    #                             'coordinateY': 31,
    #                             'coordinateZ': 30,
    #                             'id_item': 6
    #                         }
    #                     },
    #                     '1': {
    #                         'calculation_parameters': {
    #                             'lineName': '1',
    #                             'realityMM': 1.0,
    #                             'captureCount': 111,
    #                             'xStart': 593,
    #                             'yStart': 175,
    #                             'xEnd': 569,
    #                             'yEnd': 344,
    #                             'coordinateX': 67,
    #                             'coordinateY': 34,
    #                             'coordinateZ': 30,
    #                             'id_item': 6
    #                         }
    #                     }
    #                 }
    #             }
    # kq1 = CalibrationService.analyze_data_to_arrays(data)
    # print("kq1",kq1)

    # # # =========================================
    # # # test  check_calibration_data
    # # # =========================================
    # status_check = service.check_calibration_data("2","0","1",111,1110.0,0,0,0,0)
    # print(status_check)

    # # =========================================
    # # test  is_calibration_exists_check_system
    # # =========================================
    # status_check = service.is_calibration_exists_check_system(1,0)
    # print(status_check)
    # # =========================================
    # # get_calibration_dict_by_product
    # # =========================================
    # print("cha0")
    # status_get = service.get_calibration_dict_by_product(1)
    # print(status_get)
    # if status_get.ok:
    #     print("Tìm thành công")
    #     print("data",status_get.data)
    # else:
    #     print("Tìm thất bại")
if __name__ == "__main__":
    pass
    test_calibration_service()

    #  python -m app.tests.test_calibration