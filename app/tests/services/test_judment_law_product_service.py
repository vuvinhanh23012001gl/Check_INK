from app.services import JudmentLawProductSevice
from app.repository import PointRepository
from app.services import PointService
from app.repository import JudmentLawProductRepository
from app.config import (
    PATH_CONFIG_POINTS,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT,
    PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,
    BASE_DIR
)

data =  {
    "1": {
        "0": {
            "0": {},
            "1": {},
            "2": {},
            "3": {},
            "4": {
                "measurement": {}
            },
            "5": {},
            "6": {},
            "7": {},
            "8": {},
            "9": {},
            "10": {},
            "11": {},
            "12": {},
            "13": {},
            "14": {},
            "15": {},
            "16": {},
            "17": {},
            "18": {},
            "19": {},
            "20": {},
            "21": {},
            "22": {},
            "23": {},
            "24": {},
            "25": {}
        },
        "1": {
            "0": {},
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {},
            "6": {},
            "7": {},
            "8": {},
            "9": {},
            "10": {},
            "11": {},
            "12": {},
            "13": {},
            "14": {},
            "15": {},
            "16": {},
            "17": {},
            "18": {},
            "19": {},
            "20": {},
            "21": {},
            "22": {},
            "23": {},
            "24": {},
            "25": {}
        }
    }
}

def test_point_service():

    # =========================================
    # INIT
    # =========================================

    repository = PointRepository(
        
    )

    service = PointService(
        repository,
    )
    judment_repo = JudmentLawProductRepository()
    measurement = JudmentLawProductSevice(judment_repo)
    tree = service.get_point_tree_by_product_id(1)
    status_check  = measurement.compare_structure(data,tree.data)
    if status_check:
        measurement.save_data(data,tree.data)
        print("Luu thanh cong")
    print("tree",tree)
    print("data",data)
    print("check",status_check)
    result_data_product =  measurement.get_product_data("1")
    print(result_data_product.data)

def test_partial_judgment_tree_is_valid():
    """Cho phép lưu các point có inspector mà không yêu cầu mọi point.

    Input: Cây đủ ba point và payload chỉ chứa hai point đã cấu hình.
    Output: Không trả về; assert payload partial hợp lệ và khóa lạ bị từ chối.
    Errors: AssertionError nếu kiểm tra cấu trúc sai.
    """
    service = JudmentLawProductSevice(None)
    point_tree = {"1": {"0": {"0": {}, "1": {}, "2": {}}}}
    partial_payload = {
        "1": {
            "0": {
                "0": {"ArmCoverInspector": {"name": "ARM Cover"}},
                "1": {"HoleItemInspector": {"name": "Lỗ thủng"}},
            }
        }
    }

    assert service.compare_structure(partial_payload, point_tree)
    assert not service.compare_structure(
        {"1": {"0": {"9": {"ArmCoverInspector": {}}}}},
        point_tree,
    )


if __name__ == "__main__":
    test_point_service()

#python -m app.tests.services.test_judment_law_product_service