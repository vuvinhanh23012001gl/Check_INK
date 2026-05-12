import json
from pathlib import Path

class PointRepository:
    def __init__(
        self,
        path_file
    ):
        self.path_file = Path(
            path_file
        )
        # ====================
        # CREATE FOLDER
        # =====================

        self.path_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================
        # CREATE FILE
        # =====================

        if not self.path_file.exists():

            self.save_points({})

    # =========================
    # LOAD POINTS
    # =========================

    def load_points(
        self
    ) -> dict:

        if not self.path_file.exists():

            return {}

        with open(
            self.path_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # =========================
    # SAVE POINTS
    # =========================

    def save_points(
        self,
        data: dict
    ) -> None:

        with open(
            self.path_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )