from pathlib import Path
from app.model import Point
from app.repository import PointRepository
from app.core import Result,ErrorCode
from pathlib  import Path
from app.utils import Folder
import numpy as np 
from app.utils import Tool_OpenCv2
class PointService:
    def __init__( self,repository: PointRepository,path_base_patch_core:Path,path_base_img_coordinates,path_base_img_coordinates_retrain,path_base_storage):

        self.repository = repository
        self.path_base_patch_core =  path_base_patch_core
        self.path_base_img_coordinates = path_base_img_coordinates
        self.path_base_img_coordinates_retrain = path_base_img_coordinates_retrain
        self.path_base_storage =  path_base_storage

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

                    path_img_point=(
                        item.get(
                            "path_img_point"
                        )
                    ),

                    path_img_retrain = (
                        item.get(
                            "path_img_retrain"
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

    def add_point(
        self,
        product_id: int,
        point: Point,
        img: np.ndarray
    ) -> Result:
        print("Vào hàm add_point")
        if img is None or img.size == 0:
            return Result.Fail(
                ErrorCode.IMAGE_INVALID
            )
        if product_id not in self.points:
            self.points[product_id] = []
        EPSILON = 0.0001
        for existing_point in self.points[product_id]:
            if (
                abs(existing_point.x - point.x) < EPSILON
                and
                abs(existing_point.y - point.y) < EPSILON
                and
                abs(existing_point.z - point.z) < EPSILON
            ):
                return Result.Fail(
                    ErrorCode.POINT_ALREADY_EXISTS
                )
        self.points[product_id].append(
            point
        )
        index = (
            len(self.points[product_id]) - 1
        )
        product_id_str = (
            str(product_id).strip()
        )
        # =========================
        # CREATE PATH
        # ========================
        path_model_folder = (
            Path(self.path_base_patch_core)
            / product_id_str
            / str(index)
        )
        path_img_coordinate = (
            Path(self.path_base_img_coordinates)
            / product_id_str
            / f"{index}.jpg"
        )

        path_img_retrain_folder = (
            Path(self.path_base_img_coordinates_retrain)
            / product_id_str
            / str(index)
        )

        Folder.create_folder(
            path_model_folder
        )
        Folder.create_folder(
            path_img_retrain_folder
        )
        path_img_coordinate.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        Tool_OpenCv2.save_image(
            img,
            path_img_coordinate
        )
        base_batch_core = (
            Folder.get_parts_from_bottom(
                path_model_folder,
                5
            )
        )

        base_img = (
            Folder.get_parts_from_bottom(
                path_img_coordinate,
                4
            )
        )

        base_img_retrain = (
            Folder.get_parts_from_bottom(
                path_img_retrain_folder,
                5
            )
        )

        point.path_model_patch_core = (
            base_batch_core
        )

        point.path_img_point = (
            base_img
        )
        point.path_img_retrain = (
            base_img_retrain
        )

        print(
            "Full path save model:",
            path_model_folder
        )
        print(
            "Path model:",
            base_batch_core
        )
        print(
            "Full path img coordinate:",
            path_img_coordinate
        )
        print(
            "Path img coordinate:",
            base_img
        )
        print(
            "Full path retrain:",
            path_img_retrain_folder
        )
        print(
            "Path retrain:",
            base_img_retrain
        )
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
        path_img_point=None,
        path_img_retrain=None,
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

        point:Point = result_find.data

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

        if (
            path_img_point
            is not None
        ):

            point.path_img_point = (
                Path(
                    path_img_point
                )
            )
        if path_img_retrain is not None:

            point.path_img_retrain = (
                Path(path_img_retrain)
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
    def get_point_by_index(
    self,
    product_id: int,
    index_point: int
    ) -> Result:

        # =========================
        # CHECK PRODUCT
        # =========================

        arr_point = self.points.get(
            product_id
        )

        if arr_point is None:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        # =========================
        # CHECK INDEX
        # =========================

        if (
            index_point < 0
            or
            index_point >= len(arr_point)
        ):

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        # =========================
        # RETURN POINT
        # =========================

        return Result.Ok(
            arr_point[index_point]
        )

    def delete_point(
        self,
        product_id: int,
        index_point: int
    ) -> Result:
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
        point: Point = result_find.data
        if point.path_img_point:
            full_path_img = (
                Path(self.path_base_storage)
                / point.path_img_point
            )
            if full_path_img.exists():
                Folder.delete_file(
                    full_path_img
                )
            else:
                print(
                    f"Không tồn tại file: "
                    f"{full_path_img}"
                )
            print("full_path_img",full_path_img)
        if point.path_model_patch_core:
            full_path_model = (
                Path(self.path_base_storage)
                / point.path_model_patch_core
            )
            print("full_path_model",full_path_model)
            if full_path_model.exists():
                Folder.delete_folder(
                    full_path_model
                )
            else:
                print(
                    f"Không tồn tại folder model: "
                    f"{full_path_model}"
                )
        if point.path_img_retrain:

            full_path_retrain = (
                Path(self.path_base_storage)
                / point.path_img_retrain
            )
            if full_path_retrain.exists():

                Folder.delete_folder(
                    full_path_retrain
                )
            else:
                print(
                    f"Không tồn tại folder retrain: "
                    f"{full_path_retrain}"
                )
        # ========================
        # DELETE POINT
        # =========================
        deleted_point = (
            self.points[product_id].pop(
                index_point
            )
        )
        self._save_points()
        return Result.Ok(
            deleted_point
        )

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
    
    def has_path_img_point(
        self,
        point: Point
    ) -> bool:

        return (
            point.path_img_point is not None
            and
            str(
                point.path_img_point
            ).strip() != ""
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