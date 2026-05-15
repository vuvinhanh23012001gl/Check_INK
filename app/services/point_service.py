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
                    point_id=item.get("point_id", 0),
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
    
    def _generate_point_id(self) -> int:
        max_id = 0
        for arr_point in self.points.values():
            for point in arr_point:
                if point.point_id > max_id:
                    max_id = point.point_id

        return max_id + 1
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

        # =========================
        # CHECK IMAGE
        # =========================

        if img is None or img.size == 0:

            return Result.Fail(
                ErrorCode.IMAGE_INVALID
            )

        # =========================
        # CREATE PRODUCT
        # =========================

        if product_id not in self.points:

            self.points[product_id] = []

        # =========================
        # CHECK DUPLICATE POINT ID
        # =========================

        if point.point_id is not None:

            for existing_point in self.points[product_id]:

                if (
                    existing_point.point_id
                    ==
                    point.point_id
                ):

                    return Result.Fail(
                        ErrorCode.POINT_ALREADY_EXISTS
                    )

        # =========================
        # AUTO GENERATE POINT ID
        # =========================

        else:

            point.point_id = (
                self._generate_point_id()
            )

        point_id_str = str(
            point.point_id
        )

        product_id_str = str(
            product_id
        )

        # =========================
        # CREATE PATH
        # =========================

        path_model_folder = (
            Path(self.path_base_patch_core)
            / product_id_str
            / point_id_str
        )

        path_img_coordinate = (
            Path(self.path_base_img_coordinates)
            / product_id_str
            / f"{point_id_str}.jpg"
        )

        path_img_retrain_folder = (
            Path(self.path_base_img_coordinates_retrain)
            / product_id_str
            / point_id_str
        )

        # =========================
        # CREATE FOLDER
        # =========================

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

        # =========================
        # SAVE IMAGE
        # =========================

        Tool_OpenCv2.save_image(
            img,
            path_img_coordinate
        )

        # =========================
        # SAVE RELATIVE PATH
        # =========================

        point.path_model_patch_core = (
            Folder.get_parts_from_bottom(
                path_model_folder,
                5
            )
        )

        point.path_img_point = (
            Folder.get_parts_from_bottom(
                path_img_coordinate,
                4
            )
        )

        point.path_img_retrain = (
            Folder.get_parts_from_bottom(
                path_img_retrain_folder,
                5
            )
        )

        # =========================
        # APPEND
        # =========================

        self.points[product_id].append(
            point
        )

        # =========================
        # SAVE JSON
        # =========================

        self._save_points()

        return Result.Ok(point)
    # =========================
    # UPDATE POINT
    # =========================

    def update_point(
        self,
        product_id: int,
        point_id: int,

        x=None,
        y=None,
        z=None,

        path_model_patch_core=None,
        path_img_point=None,
        path_img_retrain=None,
        arr_polygon=None
    ) -> Result:

        # =========================
        # FIND POINT
        # =========================

        result_find = self.get_point_by_id(
            product_id,
            point_id
        )

        if not result_find.ok:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        point: Point = result_find.data

        # =========================
        # UPDATE XYZ
        # =========================

        if x is not None:
            point.x = x

        if y is not None:
            point.y = y

        if z is not None:
            point.z = z

        # =========================
        # UPDATE PATH MODEL
        # =========================

        if path_model_patch_core is not None:

            point.path_model_patch_core = (
                Path(path_model_patch_core)
            )

        # =========================
        # UPDATE IMAGE POINT
        # =========================

        if path_img_point is not None:

            point.path_img_point = (
                Path(path_img_point)
            )

        # =========================
        # UPDATE RETRAIN
        # =========================

        if path_img_retrain is not None:

            point.path_img_retrain = (
                Path(path_img_retrain)
            )

        # =========================
        # UPDATE POLYGON
        # =========================

        if arr_polygon is not None:

            point.arr_polygon = (
                self._normalize_polygon(
                    arr_polygon
                )
            )

        # =========================
        # SAVE
        # =========================

        self._save_points()

        return Result.Ok(point)
    # =========================
    # DELETE POINT
    # =========================
    def get_point_by_id(
        self,
        product_id: int,
        point_id: int
    ) -> Result:

        arr_point = self.points.get(
            product_id,
            []
        )

        for point in arr_point:

            if point.point_id == point_id:

                return Result.Ok(point)

        return Result.Fail(
            ErrorCode.POINT_NOT_FOUND
        )

    def delete_point(
        self,
        product_id: int,
        point_id: int
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
        # FIND POINT
        # =========================

        delete_index = -1
        point_delete = None

        for index, point in enumerate(arr_point):

            if point.point_id == point_id:

                delete_index = index
                point_delete = point
                break

        if point_delete is None:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        # =========================
        # DELETE IMAGE POINT
        # =========================

        if point_delete.path_img_point:

            full_path_img = (
                Path(self.path_base_storage)
                / point_delete.path_img_point
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

        # =========================
        # DELETE MODEL FOLDER
        # =========================

        if point_delete.path_model_patch_core:

            full_path_model = (
                Path(self.path_base_storage)
                / point_delete.path_model_patch_core
            )

            if full_path_model.exists():

                Folder.delete_folder(
                    full_path_model
                )

            else:

                print(
                    f"Không tồn tại folder model: "
                    f"{full_path_model}"
                )

        # =========================
        # DELETE RETRAIN FOLDER
        # =========================

        if point_delete.path_img_retrain:

            full_path_retrain = (
                Path(self.path_base_storage)
                / point_delete.path_img_retrain
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

        # =========================
        # DELETE POINT IN MEMORY
        # =========================

        deleted_point = (
            self.points[product_id].pop(
                delete_index
            )
        )

        # =========================
        # SAVE JSON
        # =========================

        self._save_points()

        # =========================
        # RETURN
        # =========================

        return Result.Ok(
            deleted_point
        )

    def delete_by_product_id(
        self,
        product_id: int
    ) -> Result:

        # =========================
        # CHECK PRODUCT
        # =========================

        if product_id not in self.points:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        product_id_str = str(
            product_id
        )

        # =========================
        # PATH MODEL
        # =========================

        path_model_folder = (
            Path(self.path_base_patch_core)
            / product_id_str
        )

        # =========================
        # PATH IMAGE
        # =========================

        path_img_folder = (
            Path(self.path_base_img_coordinates)
            / product_id_str
        )

        # =========================
        # PATH RETRAIN
        # =========================

        path_retrain_folder = (
            Path(self.path_base_img_coordinates_retrain)
            / product_id_str
        )

        # =========================
        # DELETE MODEL FOLDER
        # =========================

        if path_model_folder.exists():

            Folder.delete_folder(
                path_model_folder
            )

        # =========================
        # DELETE IMAGE FOLDER
        # =========================

        if path_img_folder.exists():

            Folder.delete_folder(
                path_img_folder
            )

        # =========================
        # DELETE RETRAIN FOLDER
        # =========================

        if path_retrain_folder.exists():

            Folder.delete_folder(
                path_retrain_folder
            )

        # =========================
        # DELETE PRODUCT
        # =========================

        del self.points[
            product_id
        ]

        # =========================
        # SAVE JSON
        # =========================

        self._save_points()

        # =========================
        # RETURN
        # =========================

        return Result.Ok()


    def get_dict_data(
        self
    ) -> Result:

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

    # =========================
    # CHECK MODEL PATH
    # =========================


    def has_path_model_patch_core(
        self,
        product_id: int,
        point_id: int
    ) -> bool:

        arr_point = self.points.get(
            product_id
        )

        if arr_point is None:

            return False

        for point in arr_point:

            if point.point_id == point_id:

                return (
                    point.path_model_patch_core
                    is not None
                    and
                    str(
                        point.path_model_patch_core
                    ).strip() != ""
                )

        return False


    def has_arr_polygon(
        self,
        product_id: int,
        point_id: int
    ) -> bool:

        arr_point = self.points.get(
            product_id
        )

        if arr_point is None:

            return False

        for point in arr_point:

            if point.point_id == point_id:

                return (
                    point.arr_polygon
                    is not None
                    and
                    len(
                        point.arr_polygon
                    ) > 0
                )

        return False


    # =========================
    # CHECK IMG POINT
    # =========================

    def has_path_img_point(
        self,
        product_id: int,
        point_id: int
    ) -> bool:

        arr_point = self.points.get(
            product_id
        )

        if arr_point is None:

            return False

        for point in arr_point:

            if point.point_id == point_id:
                return (
                    point.path_img_point
                    is not None
                    and
                    str(
                        point.path_img_point
                    ).strip() != ""
                )
        return False

    # =========================
    # SET ARR POLYGON
    # =========================
    
    def set_arr_polygon_by_point_id(
        self,
        product_id: int,
        point_id: int,
        arr_polygon
    ) -> Result:

        # =========================
        # FIND PRODUCT
        # =========================

        arr_point = self.points.get(
            product_id
        )

        if arr_point is None:

            return Result.Fail(
                ErrorCode.PRODUCT_NOT_FOUND
            )

        # =========================
        # FIND POINT
        # =========================

        point_find = None

        for point in arr_point:

            if point.point_id == point_id:

                point_find = point
                break

        if point_find is None:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        # =========================
        # SET POLYGON
        # =========================

        point_find.arr_polygon = (
            self._normalize_polygon(
                arr_polygon
            )
        )

        # =========================
        # SAVE
        # =========================

        self._save_points()

        return Result.Ok(
            point_find
        )
    
