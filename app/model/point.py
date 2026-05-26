from pathlib import Path
import uuid


class Point:

    def __init__(
        self,
        point_id: int,
        x:int,
        y:int,
        z:int,


        path_model_patch_core: str | Path | None = None,
        path_img_point: str | Path | None = None,
        path_img_retrain: str | Path | None = None,

        arr_polygon: list | None = None
    ):

        # =========================
        # POINT ID
        # =========================

        self._point_id = point_id

        # =========================
        # XYZ
        # =========================

        self._x = x
        self._y = y
        self._z = z

        # =========================
        # PATH MODEL
        # =========================

        self._path_model_patch_core = (
            Path(path_model_patch_core)
            if path_model_patch_core
            else None
        )

        # =========================
        # PATH IMG POINT
        # =========================

        self._path_img_point = (
            Path(path_img_point)
            if path_img_point
            else None
        )

        # =========================
        # PATH IMG RETRAIN
        # =========================

        self._path_img_retrain = (
            Path(path_img_retrain)
            if path_img_retrain
            else None
        )

        # =========================
        # POLYGON
        # =========================

        self._arr_polygon = (
            arr_polygon
            if arr_polygon
            else []
        )

    # =========================
    # POINT ID
    # =========================

    @property
    def point_id(self) -> int:
        return self._point_id

    @point_id.setter
    def point_id(self, value: int):
        self._point_id = value

    # =========================
    # X
    # =========================

    @property
    def x(
        self
    ) -> float:

        return self._x

    @x.setter
    def x(
        self,
        value: float
    ) -> None:

        self._x = value

    # =========================
    # Y
    # =========================

    @property
    def y(
        self
    ) -> float:

        return self._y

    @y.setter
    def y(
        self,
        value: float
    ) -> None:

        self._y = value

    # =========================
    # Z
    # =========================

    @property
    def z(
        self
    ) -> float:

        return self._z

    @z.setter
    def z(
        self,
        value: float
    ) -> None:

        self._z = value

    # =========================
    # PATH MODEL PATCH CORE
    # =========================

    @property
    def path_model_patch_core(
        self
    ) -> Path | None:

        return self._path_model_patch_core

    @path_model_patch_core.setter
    def path_model_patch_core(
        self,
        value: str | Path | None
    ) -> None:

        self._path_model_patch_core = (
            Path(value)
            if value
            else None
        )

    # =========================
    # PATH IMG POINT
    # =========================

    @property
    def path_img_point(
        self
    ) -> Path | None:

        return self._path_img_point

    @path_img_point.setter
    def path_img_point(
        self,
        value: str | Path | None
    ) -> None:

        self._path_img_point = (
            Path(value)
            if value
            else None
        )

    # =========================
    # PATH IMG RETRAIN
    # =========================

    @property
    def path_img_retrain(
        self
    ) -> Path | None:

        return self._path_img_retrain

    @path_img_retrain.setter
    def path_img_retrain(
        self,
        value: str | Path | None
    ) -> None:

        self._path_img_retrain = (
            Path(value)
            if value
            else None
        )

    # =========================
    # ARR POLYGON
    # =========================

    @property
    def arr_polygon(
        self
    ) -> list:

        return self._arr_polygon

    @arr_polygon.setter
    def arr_polygon(
        self,
        arr_polygon: list
    ) -> None:

        self._arr_polygon = arr_polygon

    # =========================
    # TO DICT
    # =========================

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,

            "path_model_patch_core": (
                str(self.path_model_patch_core)
                if self.path_model_patch_core
                else None
            ),

            "path_img_point": (
                str(self.path_img_point)
                if self.path_img_point
                else None
            ),

            "path_img_retrain": (
                str(self.path_img_retrain)
                if self.path_img_retrain
                else None
            ),

            "arr_polygon": self.arr_polygon
        }
    # =========================
    # REPR
    # =========================

    def __repr__(self) -> str:
        return (
            f"Point("
            f"point_id={self.point_id}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"path_model_patch_core={self.path_model_patch_core}, "
            f"path_img_point={self.path_img_point}, "
            f"path_img_retrain={self.path_img_retrain}, "
            f"arr_polygon={self.arr_polygon}"
            f")"
        )