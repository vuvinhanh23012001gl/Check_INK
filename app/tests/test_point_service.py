from app.model import Point
from app.repository import PointRepository
from app.services import PointService
from app.utils import Folder
from app.config import (
    PATH_CONFIG_POINTS,
    PATH_FOLDER_MODEL_DETECT_PATCH_CORE
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
    obj_folder = Folder()

    service = PointService(
        obj_folder,
        repository,
        PATH_FOLDER_MODEL_DETECT_PATCH_CORE
    )

    # =========================
    # CREATE POINT
    # =========================
    point = Point(
        x=100,
        y=100,
        z=300,
    )


    # point = Point(
    #     x=101,
    #     y=200,
    #     z=300,
    #     arr_polygon=[
    #         [(10, 10), (100, 10), (100, 100)],
    #         [(200, 200), (300, 200), (300, 300)]
    #     ]
    # )

    # =========================
    # ADD
    # =========================
    # res_add = service.add_point(product_id=1, point=point)
    # print_result("ADD POINT", res_add)

    # # =========================
    # # GET
    # # =========================
    # res_get = service.get_points_by_product_id(0)
    # print_result("GET POINTS", res_get)

    # # =========================
    # # UPDATE
    # # =========================

    # res_update = service.update_point(
    #         product_id=5,
    #         index_point=0,
    #         x=999,
    #         y=888,
    #         z=777,
    #         arr_polygon=[[(1, 1), (2, 2), (3, 3)]]
    #     )
    # print_result("UPDATE POINT", res_update)

    # # =========================
    # # DELETE
    # # =========================
    # res_delete = service.delete_point(product_id=2, index_point=0)
    # print_result("DELETE POINT", res_delete)

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
    index = service.get_point_index_by_xyz(2,100,200,300)
    print(index)
if __name__ == "__main__":
    test_point_service()