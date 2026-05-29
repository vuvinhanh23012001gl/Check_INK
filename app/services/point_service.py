from pathlib import Path
from app.model import Point
from app.repository import PointRepository
from app.core import Result, ErrorCode
from app.utils import Folder
from app.utils import Tool_OpenCv2
import numpy as np

class PointService:
    def __init__(
        self,
        repository: PointRepository,
        path_base_patch_core: Path,
        path_base_img_coordinates,
        path_base_img_coordinates_retrain,
        path_base_storage
    ):

        self.repository = repository

        self.path_base_patch_core = (
            path_base_patch_core
        )

        self.path_base_img_coordinates = (
            path_base_img_coordinates
        )

        self.path_base_img_coordinates_retrain = (
            path_base_img_coordinates_retrain
        )

        self.path_base_storage = (
            path_base_storage
        )

        self.points = (
            self._load_points()
        )

    # =====================================
    # LOAD
    # =====================================

    def _load_points(self) -> dict:

        raw_data = (
            self.repository.load_points()
        )

        points = {}

        if not isinstance(raw_data, dict):

            return {}

        for product_id, frame_dict in (
            raw_data.items()
        ):

            product_id = int(product_id)

            points[product_id] = {}

            if not isinstance(frame_dict, dict):

                continue

            for frame_id, point_dict in (
                frame_dict.items()
            ):

                frame_id = int(frame_id)

                points[
                    product_id
                ][
                    frame_id
                ] = {}

                if not isinstance(point_dict, dict):

                    continue

                for point_id, item in (
                    point_dict.items()
                ):

                    point_id = int(point_id)

                    point = Point(

                        point_id=point_id,

                        x=item.get(
                            "x",
                            0
                        ),

                        y=item.get(
                            "y",
                            0
                        ),

                        z=item.get(
                            "z",
                            0
                        ),

                        path_model_patch_core=item.get(
                            "path_model_patch_core"
                        ),

                        path_img_point=item.get(
                            "path_img_point"
                        ),

                        path_img_retrain=item.get(
                            "path_img_retrain"
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
                        product_id
                    ][
                        frame_id
                    ][
                        point_id
                    ] = point

        return points
    
    # =====================================
    # CHECK PRODUCT + POINT EXISTS
    # =====================================

    def is_exists_product_frame_point_id(
        self,
        product_id: int,
        frame_id: int,
        point_id: int
    ) -> bool:

        if product_id not in self.points:
            return False

        if frame_id not in self.points[product_id]:
            return False

        frame_dict = self.points[product_id][frame_id]

        return point_id in frame_dict
    # =====================================
    # SAVE
    # =====================================

    def _save_points(self) -> None:
        data = {}
        for product_id, frame_dict in (
            self.points.items()
        ):
            data[str(product_id)] = {}
            for frame_id, point_dict in (
                frame_dict.items()
            ):
                data[
                    str(product_id)
                ][
                    str(frame_id)
                ] = {}

                for point_id, point in (
                    point_dict.items()
                ):

                    data[
                        str(product_id)
                    ][
                        str(frame_id)
                    ][
                        str(point_id)
                    ] = point.to_dict()

        self.repository.save_points(
            data
        )

    # =====================================
    # GENERATE ID
    # =====================================

    def _generate_point_id(self) -> int:

        max_id = 0

        for frame_dict in (
            self.points.values()
        ):

            for point_dict in (
                frame_dict.values()
            ):

                for point_id in (
                    point_dict.keys()
                ):

                    if point_id > max_id:

                        max_id = point_id

        return max_id + 1

    # =====================================
    # NORMALIZE POLYGON
    # =====================================

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

    # =====================================
    # GET PRODUCT
    # =====================================

    def get_points_by_product_id_obj_point(
        self,
        product_id: int
    ) -> Result:

        return Result.Ok(

            self.points.get(
                product_id,
                {}
            )
        )
    
    
    def get_points_by_product_id(
        self,
        product_id: int
    ) -> Result:
        product = self.points.get(product_id)
        if not product:
            return Result.Fail(ErrorCode.PRODUCT_NOT_FOUND)
        data = {}
        for frame_id, frame_dict in product.items():
            data[str(frame_id)] = {}
            for point_id, point in frame_dict.items():
                data[str(frame_id)][str(point_id)] = point.to_dict()
        return Result.Ok(data)
    
    # =====================================
    # GET FRAME
    # =====================================

    def get_points_by_frame_id(
        self,
        product_id: int,
        frame_id: int
    ) -> Result:

        point_dict = (

            self.points
            .get(product_id, {})
            .get(frame_id, {})

        )

        return Result.Ok(
            point_dict
        )

    # =====================================
    # GET POINT
    # =====================================

    def get_point_by_id(
        self,
        product_id: int,
        frame_id: int,
        point_id: int
    ) -> Result:

        point = (

            self.points
            .get(product_id, {})
            .get(frame_id, {})
            .get(point_id)

        )

        if point is None:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        return Result.Ok(point)

    # =====================================
    # ADD POINT
    # =====================================

    def add_point(
        self,
        product_id: int,
        frame_id: int,
        point: Point,
        img: np.ndarray
    ) -> Result:
        point.x
        # =====================================
        # VALIDATE PRODUCT_ID
        # =====================================
    
        if not isinstance(
            product_id,
            int
        ):
            if isinstance(
                product_id,
                str
            ):
                try:
                    product_id = int(
                        product_id
                    )
                except Exception:
                    return Result.Fail(
                        ErrorCode.PRODUCT_ID_INVALID
                    )
            else:
                return Result.Fail(
                    ErrorCode.PRODUCT_ID_INVALID
                )
        if not isinstance(
            frame_id,
            int
        ):
            if isinstance(
                frame_id,
                str
            ):
                try:
                    frame_id = int(
                        frame_id
                    )
                except Exception:
                    return Result.Fail(
                        ErrorCode.FRAME_ID_INVALID
                    )
            else:
                return Result.Fail(
                    ErrorCode.FRAME_ID_INVALID
                )
        if not isinstance(
            point.x,
            int
        ):
            if isinstance(
                point.x,
                str
            ):
                try:
                    point.x = int(
                        point.x
                    )
                except Exception:
                    return Result.Fail(
                        ErrorCode.POINT_X_INVALID
                    )
            else:
                return Result.Fail(
                    ErrorCode.POINT_X_INVALID
                )
        if not isinstance(
            point.y,
            int
        ):
            if isinstance(
                point.y,
                str
            ):
                try:
                    point.y = int(
                        point.y
                    )
                except Exception:
                    return Result.Fail(
                        ErrorCode.POINT_Y_INVALID
                    )
            else:
                return Result.Fail(
                    ErrorCode.POINT_Y_INVALID
                )
        if not isinstance(
            point.z,
            int
        ):
            if isinstance(
                point.z,
                str
            ):
                try:
                    point.z = int(
                        point.z
                    )
                except Exception:
                    return Result.Fail(
                        ErrorCode.POINT_Z_INVALID
                    )
            else:
                return Result.Fail(
                    ErrorCode.POINT_Z_INVALID
                )
            
        if img is None or img.size == 0:

            return Result.Fail(
                ErrorCode.IMAGE_INVALID
            )

        if product_id not in self.points:

            self.points[product_id] = {}

        if frame_id not in self.points[product_id]:

            self.points[product_id][frame_id] = {}

        if point.point_id is None:

            point.point_id = (
                self._generate_point_id()
            )

        if point.point_id in (

            self.points[product_id][frame_id]

        ):

            return Result.Fail(
                ErrorCode.POINT_ALREADY_EXISTS
            )
        product_id_str = str(product_id)
        frame_id_str = str(frame_id)
        point_id_str = str(point.point_id)
        path_model_folder = (
            Path(self.path_base_patch_core)
            / product_id_str
            / frame_id_str
            / point_id_str
        )
        path_img_coordinate = (
            Path(self.path_base_img_coordinates)
            / product_id_str
            / frame_id_str
            / f"{point_id_str}.jpg"
        )
        path_img_retrain_folder = (
            Path(
                self.path_base_img_coordinates_retrain
            )
            / product_id_str
            / frame_id_str
            / point_id_str
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
        point.path_model_patch_core = (
            Folder.get_parts_from_bottom(
                path_model_folder,
                6
            )
        )
        point.path_img_point = (

            Folder.get_parts_from_bottom(
                path_img_coordinate,
                5
            )
        )
        point.path_img_retrain = (

            Folder.get_parts_from_bottom(
                path_img_retrain_folder,
                6
            )
        )
        self.points[
            product_id
        ][
            frame_id
        ][
            point.point_id
        ] = point
        self._save_points()
        return Result.Ok(point)

    # =====================================
    # UPDATE POINT
    # =====================================

    def update_point(
        self,
        product_id: int,
        frame_id: int,
        point_id: int,
        x,
        y,
        z,
        img
    ) -> Result:
        result_find = self.get_point_by_id(
            product_id,
            frame_id,
            point_id
        )
        print(product_id,frame_id,point_id)
        if not result_find.ok:
            return Result.Fail(ErrorCode.POINT_NOT_FOUND)
        point: Point = result_find.data
        # =====================================
        # UPDATE XYZ
        # =====================================
        if x is not None:
            point.x = x
        if y is not None:
            point.y = y
        if z is not None:
            point.z = z
        # =====================================
        # UPDATE IMAGE
        # =====================================
        if img is not None:
            if img.size == 0:
                return Result.Fail(ErrorCode.IMAGE_INVALID)
            product_id_str = str(product_id)
            frame_id_str = str(frame_id)
            point_id_str = str(point_id)
            full_path = (
                Path(self.path_base_img_coordinates)
                / product_id_str
                / frame_id_str
                / f"{point_id_str}.jpg"
            )
            if full_path.exists():
                full_path.unlink()
            full_path.parent.mkdir(parents=True, exist_ok=True)
            Tool_OpenCv2.save_image(img, full_path)
            point.path_img_point = Folder.get_parts_from_bottom(
                full_path,
                5
            )
        self._save_points()
        return Result.Ok(point)
    
    
    def update_point_polygon(
        self,
        product_id: int,
        frame_id: int,
        point_id: int,
        arr_polygon
    ) -> Result:
        # update polygon
        result_find = self.get_point_by_id(
            product_id,
            frame_id,
            point_id
        )
        if not result_find.ok:
            return Result.Fail(ErrorCode.POINT_NOT_FOUND)
        point: Point = result_find.data
        point.arr_polygon = self._normalize_polygon(arr_polygon)
        self._save_points()
        return Result.Ok(point)
    # =====================================
    # DELETE POINT
    # =====================================

    def delete_point(
        self,
        product_id: int,
        frame_id: int,
        point_id: int
    ) -> Result:

        point_delete = (

            self.points
            .get(product_id, {})
            .get(frame_id, {})
            .get(point_id)

        )

        if point_delete is None:

            return Result.Fail(
                ErrorCode.POINT_NOT_FOUND
            )

        # =====================================
        # DELETE IMG
        # =====================================

        if point_delete.path_img_point:

            full_path_img = (

                Path(self.path_base_storage)

                / point_delete.path_img_point
            )

            if full_path_img.exists():

                Folder.delete_file(
                    full_path_img
                )

        # =====================================
        # DELETE MODEL
        # =====================================

        if point_delete.path_model_patch_core:

            full_path_model = (

                Path(self.path_base_storage)

                / point_delete.path_model_patch_core
            )

            if full_path_model.exists():

                Folder.delete_folder(
                    full_path_model
                )

        # =====================================
        # DELETE RETRAIN
        # =====================================

        if point_delete.path_img_retrain:

            full_path_retrain = (

                Path(self.path_base_storage)

                / point_delete.path_img_retrain
            )

            if full_path_retrain.exists():

                Folder.delete_folder(
                    full_path_retrain
                )

        # =====================================
        # DELETE MEMORY
        # =====================================

        del self.points[
            product_id
        ][
            frame_id
        ][
            point_id
        ]

        self._save_points()

        return Result.Ok(
            point_delete
        )
    
    