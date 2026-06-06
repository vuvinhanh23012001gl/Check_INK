from app.repository import CalibrationReponsitory
from app.services import CalibrationService, PointService

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
    frame_id = 0

    calibration_data = {
        "reality_mm": 100.0,
        "pixel_mean": 500.0,
        "pixel_std": 2.5,
        "calibration_mm_per_pixel": 0.2,
        "number_capture": 10
    }

    # # =========================================
    # # ADD
    # # =========================================

    # result = service.add_calibration(
    #     product_id,
    #     frame_id,
    #     calibration_data
    # )

    # print_result(
    #     "ADD CALIBRATION",
    #     result
    # )

    # # =========================================
    # # GET
    # # =========================================

    # result = service.get_calibration(
    #     product_id,
    #     frame_id
    # )
    # if result.ok:
    #     calibration = result.data
    #     print("\nReality mm:", calibration.reality_mm)
    #     print("Pixel mean:", calibration.pixel_mean)
    #     print("Pixel std:", calibration.pixel_std)
    #     print("CV %:", calibration.cv_percent)

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

    # result = service.update_calibration(
    #     product_id,
    #     frame_id,
    #     update_data
    # )

    # print_result(
    #     "UPDATE CALIBRATION",
    #     result
    # )

    # # =========================================
    # # GET AFTER UPDATE
    # # =========================================

    # result = service.get_calibration(
    #     product_id,
    #     frame_id
    # )

    # print_result(
    #     "GET AFTER UPDATE",
    #     result
    # )

    # # =========================================
    # # DELETE
    # # =========================================

    # result = service.delete_calibration(
    #     1,
    #     0
    # )

    # print_result(
    #     "DELETE CALIBRATION",
    #     result
    # )

    # # =========================================
    # # GET AFTER DELETE
    # # =========================================

    # result = service.get_calibration(
    #     product_id,
    #     frame_id
    # )

    # print_result(
    #     "GET AFTER DELETE",
    #     result
    # )


# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    test_calibration_service()

    # python -m app.tests.test_calibration_service