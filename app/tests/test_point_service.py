from app.model import Point
from app.repository import PointRepository
from app.services import PointService
from app.config import (
    PATH_CONFIG_POINTS,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE,PATH_FOLDER_IMG_COORDINATE_PRODUCT,PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,BASE_DIR
)


def print_result(title, result):
    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)
    print("OK:", result.ok)
    print("DATA:", result.data)
    print("ERROR:", result.error)


def test_point_service():
    # =========================
    # INIT
    # =========================
    repository = PointRepository(PATH_CONFIG_POINTS)


    service = PointService(
        repository,
        PATH_FOLDER_MODEL_DETECT_PATCH_CORE,PATH_FOLDER_IMG_COORDINATE_PRODUCT,PATH_FOLDER_IMG_COORDINATE_PRODUCT_RETRAIN,BASE_DIR
    )
    # =========================
    # CREATE POINT
    # =========================
    point = Point(
        x=310,
        y=200,
        z=300,
        arr_polygon=[
            [(10, 10), (100, 10), (100, 100)],
            [(200, 200), (300, 200), (300, 300)]
        ]
    )

    # # =========================
    # # ADD
    # # =========================
    # import numpy as np
    # img = np.zeros(
    #     (100, 100, 3),
    #     dtype=np.uint8
    # )

    # res_add = service.add_point(product_id=1, point=point, img =  img)
    # print_result("ADD POINT", res_add)



    # # =========================
    # # GET
    # # =========================
    # res_get = service.get_points_by_product_id(1)
    # print_result("GET POINTS", res_get)

    # # =========================
    # # UPDATE
    # # =========================
    # id = 1
    # res_get = service.get_points_by_product_id(id)
    # print_result("GET POINTS", res_get)
    # res_update = service.update_point(
    #         product_id=id,
    #         index_point=0,
    #         x=9299,
    #         y=888,
    #         z=777,
    #         arr_polygon=[[(2, 1), (2, 2), (3, 3)]]
    #     )
    # print_result("UPDATE POINT", res_update)

    # # =========================
    # # DELETE
    # # =========================
    
    res_delete = service.delete_point(product_id = 1, index_point = 0)
    print_result("DELETE POINT", res_delete)

    # # # =========================
    # # # FINAL STATE
    # # # =========================
    # res_final = service.get_dict_data()
    # print_result("FINAL DATA", res_final)

    # # # =========================
    # # # delete_all_points_by_product_id
    # # # =========================
    # delete_all = service.delete_all_points_by_product_id(1)
    # print_result("delete_all id", delete_all)
    # # # =========================
    # # # test arr polygon add
    # # # =========================
    #     id = 2
    #     res_polygon = service.set_arr_polygon_by_point(
    #     product_id=id,
    #     index_point=0,
    #     arr_polygon=[
    #         [[0, 0], [0, 4], [3, 3]]
    #     ]
    # )
    #     print_result("ADD POLYGON", res_polygon)
    #     # 3. get lại data
    #     res_get = service.get_points_by_product_id(id)
    #     print_result("GET POINTS AFTER POLYGON", res_get)
    # # # =========================
    # # # test find_point_index
    # # # =========================
    # index = service.get_point_index_by_xyz(2,100,200,300)
    # print(index)
if __name__ == "__main__":
    test_point_service()