import json
import os
from .base_config import BaseConfig


class IAIConfig(BaseConfig):

    def __init__(self, path_config_iai: str):

        self.path_config_iai = path_config_iai

        # =========================
        # LIMIT X
        # =========================
        self.limit_x_min = 0
        self.limit_x_max = 1000

        # =========================
        # LIMIT Y
        # =========================
        self.limit_y_min = 0
        self.limit_y_max = 1000

        # =========================
        # LIMIT Z
        # =========================
        self.limit_z_min = 0
        self.limit_z_max = 1000

        # =========================
        # HOME POSITION
        # =========================
        self.home_x = 0
        self.home_y = 0
        self.home_z = 0

        self.load()

    # ==========================================================
    # LOAD CONFIG
    # ==========================================================
    def load(self):

        # Nếu chưa có file config thì tạo mới
        if not os.path.exists(self.path_config_iai):
            self.save()
            return

        with open(self.path_config_iai, "r", encoding="utf-8") as file:
            data = json.load(file)

        # =========================
        # LIMIT X
        # =========================
        self.limit_x_min = data.get(
            "limit_x_min",
            self.limit_x_min
        )

        self.limit_x_max = data.get(
            "limit_x_max",
            self.limit_x_max
        )

        # =========================
        # LIMIT Y
        # =========================
        self.limit_y_min = data.get(
            "limit_y_min",
            self.limit_y_min
        )

        self.limit_y_max = data.get(
            "limit_y_max",
            self.limit_y_max
        )

        # =========================
        # LIMIT Z
        # =========================
        self.limit_z_min = data.get(
            "limit_z_min",
            self.limit_z_min
        )

        self.limit_z_max = data.get(
            "limit_z_max",
            self.limit_z_max
        )

        # =========================
        # HOME POSITION
        # =========================
        self.home_x = data.get(
            "home_x",
            self.home_x
        )

        self.home_y = data.get(
            "home_y",
            self.home_y
        )

        self.home_z = data.get(
            "home_z",
            self.home_z
        )

    # ==========================================================
    # SAVE CONFIG
    # ==========================================================
    def save(self):

        data = {

            # =========================
            # LIMIT X
            # =========================
            "limit_x_min": self.limit_x_min,
            "limit_x_max": self.limit_x_max,

            # =========================
            # LIMIT Y
            # =========================
            "limit_y_min": self.limit_y_min,
            "limit_y_max": self.limit_y_max,

            # =========================
            # LIMIT Z
            # =========================
            "limit_z_min": self.limit_z_min,
            "limit_z_max": self.limit_z_max,

            # =========================
            # HOME POSITION
            # =========================
            "home_x": self.home_x,
            "home_y": self.home_y,
            "home_z": self.home_z
        }

        with open(self.path_config_iai, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )
    def get_dict(self) -> dict:
        return {

            # =========================
            # LIMIT X
            # =========================
            "limit_x_min": self.limit_x_min,
            "limit_x_max": self.limit_x_max,

            # =========================
            # LIMIT Y
            # =========================
            "limit_y_min": self.limit_y_min,
            "limit_y_max": self.limit_y_max,

            # =========================
            # LIMIT Z
            # =========================
            "limit_z_min": self.limit_z_min,
            "limit_z_max": self.limit_z_max,

            # =========================
            # HOME POSITION
            # =========================
            "home_x": self.home_x,
            "home_y": self.home_y,
            "home_z": self.home_z
        }