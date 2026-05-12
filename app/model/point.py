from pathlib import Path

class Point:

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        path_model_patch_core: str | Path | None = None,
        arr_polygon: list | None = None
    ):

        self._x = x
        self._y = y
        self._z = z

        self._path_model_patch_core = (
            Path(path_model_patch_core)
            if path_model_patch_core
            else None
        )

        self._arr_polygon = (
            arr_polygon
            if arr_polygon
            else []
        )

    # =========================
    # X
    # =========================
    @property
    def x(self) -> float:
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
    def y(self) -> float:
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
    def z(self) -> float:
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
    def to_dict(
        self
    ) -> dict:

        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,

            "path_model_patch_core": (
                str(self.path_model_patch_core)
                if self.path_model_patch_core
                else None
            ),

            "arr_polygon": (
                self.arr_polygon
            )
        }

    # =========================
    # REPR
    # =========================
    def __repr__(
        self
    ) -> str:

        return (
            f"Point("
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"path_model_patch_core="
            f"{self.path_model_patch_core}, "
            f"arr_polygon="
            f"{self.arr_polygon}"
            f")"
        )
    



# from pathlib import Path
# from point import Point
# def test_point():
#     point = Point(
#         x=100,
#         y=200,
#         z=50,
#         path_model_patch_core=(
#             "models/patch_core/model.onnx"
#         ),

#         arr_polygon=[
#             [(10, 10), (100, 10), (100, 100)],
#             [(200, 200), (300, 200), (300, 300)]
#         ]
#     )
#     # =========================
#     # PRINT
#     # =========================
#     print(point)
#     # =========================
#     # PROPERTY
#     # =========================
#     print(point.x)
#     print(point.y)
#     print(point.z)

#     print(
#         point.path_model_patch_core
#     )

#     print(
#         point.arr_polygon
#     )

#     # =========================
#     # SET
#     # =========================
#     point.x = 999

#     point.path_model_patch_core = (
#         Path(
#             "models/new_model.onnx"
#         )
#     )

#     point.arr_polygon = [
#         [(1, 1), (2, 2), (3, 3)]
#     ]

#     # =========================
#     # PRINT AFTER SET
#     # =========================
#     print(point)

#     # =========================
#     # TO DICT
#     # =========================
#     dict_data = (
#         point.to_dict()
#     )

#     print(dict_data)


# if __name__ == "__main__":
#     test_point()
