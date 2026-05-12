from pathlib import Path
from app.model import Point
from app.repository import PointRepository
from app.core import Result,ErrorCode
from pathlib  import Path
from app.utils import Folder

class PointService:
    def __init__( self,obj_folder:Folder,repository: PointRepository,path_base_patch_core:Path):
        self.repository = repository
        self.obj_folder = obj_folder
        self.path_base_patch_core =  path_base_patch_core

        self.points = (
            self._load_points()
        )
    # =========================
    # LOAD
    # =========================
    def _load_points(
        self
    ) -> dict:
        raw_data = (
            self.repository.load_points()
        )
        points = {}
        for product_id, arr_point in (
            raw_data.items()
        ):
            points[
                int(product_id)
            ] = []
            for item in arr_point:
                point = Point(
                    x=item.get("x", 0),
                    y=item.get("y", 0),
                    z=item.get("z", 0),
                    path_model_patch_core=(
                        item.get(
                            "path_model_patch_core"
                        )
                    ),
                    arr_polygon=(
                        self._normalize_polygon(
                            item.get(
                                "arr_polygon",
                                []
                            )
                        )
                    )
                )
                points[
                    int(product_id)
                ].append(point)
        return points

    # ========================
    # SAVE
    # =========================
    def _save_points(
        self
    ) -> None:
        data = {}
        for product_id, arr_point in (
            self.points.items()
        ):
            data[str(product_id)] = [
                point.to_dict()
                for point in arr_point
            ]
        self.repository.save_points(
            data
        )
    # =========================
    # NORMALIZE POLYGON
    # =========================

    def _normalize_polygon(
        self,
        arr_polygon
    ):
        output = []
        for polygon in arr_polygon:
            arr_point = []
            for point in polygon:
                arr_point.append(
                    tuple(point)
                )
            output.append(
                arr_point
            )
        return output

    # =========================
    # GET POINTS
    # =========================

    def get_points_by_product_id(
        self,
        product_id: int
    ):
        arr_point = self.points.get(
            product_id,
            []
        )
        return Result.Ok(
            arr_point
        )
    # =========================
    # GET POINT
    # =========================

    def get_point_by_index(
        self,
        product_id: int,
        index_point: int
    ):
        arr_point = self.points.get(
            product_id
        )

        if not arr_point:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        if (
            index_point < 0
            or
            index_point >= len(arr_point)
        ):

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        return Result.Ok(
            arr_point[index_point]
        )

    # =========================
    # ADD POINT
    # =========================

    def add_point(self, product_id: int, point: Point):

        if product_id not in self.points:
            self.points[product_id] = []
        else:
            # CHECK DUPLICATE
            for existing_point in self.points[product_id]:
                if (
                    existing_point.x == point.x and
                    existing_point.y == point.y and
                    existing_point.z == point.z
                ):
                    return Result.Fail(
                        ErrorCode.POINT_ALREADY_EXISTS
                    )

        # thêm point mới
        self.points[product_id].append(point)

        index = len(self.points[product_id]) - 1

        path_model_folder = (
            Path(self.path_base_patch_core)
            / str(product_id).strip()
            / str(index)
        )

        self.obj_folder.create_folder(path_model_folder)

        base = self.obj_folder.get_parts_from_bottom(path_model_folder, 5)
        point.path_model_patch_core = base

        print(base)
        print(path_model_folder)

        self._save_points()

        return Result.Ok(point)
           
    # =========================
    # UPDATE POINT
    # =========================

    def update_point(
        self,
        product_id: int,
        index_point: int,

        x=None,
        y=None,
        z=None,

        path_model_patch_core=None,

        arr_polygon=None
    ):

        result_find = (
            self.get_point_by_index(
                product_id,
                index_point
            )
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        point = result_find.data

        # =====================
        # UPDATE
        # =====================

        if x is not None:

            point.x = x

        if y is not None:

            point.y = y

        if z is not None:

            point.z = z

        if (
            path_model_patch_core
            is not None
        ):

            point.path_model_patch_core = (
                Path(
                    path_model_patch_core
                )
            )

        if arr_polygon is not None:

            point.arr_polygon = (
                self._normalize_polygon(
                    arr_polygon
                )
            )

        # =====================
        # SAVE
        # =====================
        
        self._save_points()

        return Result.Ok(point)

    # =========================
    # DELETE POINT
    # =========================

    def delete_point(
        self,
        product_id: int,
        index_point: int
    ):

        result_find = (
            self.get_point_by_index(
                product_id,
                index_point
            )
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        deleted_point = (
            self.points[
                product_id
            ].pop(index_point)
        )

        self._save_points()

        return Result.Ok(
            deleted_point
        )

    # =========================
    # DELETE ALL POINT
    # =========================

    def delete_all_points_by_product_id(
        self,
        product_id: int
    ):

        if product_id in self.points:

            del self.points[
                product_id
            ]

            self._save_points()

        return Result.Ok()

    # =========================
    # TO DICT
    # =========================

    def get_dict_data(
        self
    ):

        output = {}

        for product_id, arr_point in (
            self.points.items()
        ):

            output[
                product_id
            ] = [

                point.to_dict()

                for point in arr_point
            ]

        return Result.Ok(
            output
        )
    
    def has_path_model_patch_core(self, point: Point) -> bool:
        return (
            point.path_model_patch_core is not None
            and str(point.path_model_patch_core).strip() != ""
        )
    
    def has_arr_polygon(self, point: Point) -> bool:
        return (
            point.arr_polygon is not None
            and len(point.arr_polygon) > 0
        )
    

    def set_arr_polygon_by_point(
        self,
        product_id: int,
        index_point: int,
        arr_polygon
    ):
        # =========================
        # FIND POINT
        # =========================
        result_find: Result = self.get_point_by_index(
            product_id,
            index_point
        )

        if not result_find.ok:
            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        point: Point = result_find.data

        # =========================
        # NORMALIZE + SET (NOT APPEND)
        # =========================
        point.arr_polygon = self._normalize_polygon(
            arr_polygon
        )

        # =========================
        # SAVE
        # =========================
        self._save_points()

        return Result.Ok(point)
    
    # ham duoi chua chuan cho lam
    def get_point_index_by_xyz(
        self,
        product_id: int,
        x: float,
        y: float,
        z: float
    ) -> int:

        arr_point = self.points.get(product_id, [])

        for idx, point in enumerate(arr_point):
            if point.x == x and point.y == y and point.z == z:
                return idx

        return -1