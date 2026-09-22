import json
import os
from enum import Enum
from .base_config import BaseConfig
from app.config import PATH_FILE_DATA_CONFIG_IAI

class ModeState(Enum):
    NORMOL = 0
    PAUSE = 1
    STOP = 2
    WAIT_ORG = 3
    WAIT_ORIGIN_SENSOR = 16
    RETURNED_OR = 4
    WAIT_AUTO = 5
    AUTO = 6
    TOUCH_SAFETY = 8
    WAIT_TAKE_PRODUCT = 9
    PUT_PRODUCT = 10
    RUN_STEP = 11
    RUN_STEP_1 = 12
    RUN_STEP_3 = 14
    RUN_STEP_4 = 15

class IAIConfig(BaseConfig):
    def __init__(self):
        self.path_config_iai = PATH_FILE_DATA_CONFIG_IAI
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
        self.command_status = "status_all:"
        self.command_move_to_origin = "move_to_org:"
        self.command_stop = "stop:"
        self.command_reset_stop = "refesh_stop:"
        self.command_pause = "pause:"
        self.command_resume = "refesh_pause:"
        self.status_returned_origin = "has_returned_org:"
        self.input_poll_interval = 0.05
        self.queue_timeout = 0.01
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
        self.command_status = data.get("command_status", self.command_status)
        self.command_move_to_origin = data.get(
            "command_move_to_origin", self.command_move_to_origin
        )
        self.command_stop = data.get("command_stop", self.command_stop)
        self.command_reset_stop = data.get(
            "command_reset_stop", self.command_reset_stop
        )
        self.command_pause = data.get("command_pause", self.command_pause)
        self.command_resume = data.get("command_resume", self.command_resume)
        self.status_returned_origin = data.get(
            "status_returned_origin", self.status_returned_origin
        )
        self.input_poll_interval = data.get(
            "input_poll_interval", self.input_poll_interval
        )
        self.queue_timeout = data.get("queue_timeout", self.queue_timeout)

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
            "home_z": self.home_z,
            "command_status": self.command_status,
            "command_move_to_origin": self.command_move_to_origin,
            "command_stop": self.command_stop,
            "command_reset_stop": self.command_reset_stop,
            "command_pause": self.command_pause,
            "command_resume": self.command_resume,
            "status_returned_origin": self.status_returned_origin,
            "input_poll_interval": self.input_poll_interval,
            "queue_timeout": self.queue_timeout
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
            "home_z": self.home_z,
            "command_status": self.command_status,
            "command_move_to_origin": self.command_move_to_origin,
            "command_stop": self.command_stop,
            "command_reset_stop": self.command_reset_stop,
            "command_pause": self.command_pause,
            "command_resume": self.command_resume,
            "status_returned_origin": self.status_returned_origin,
            "input_poll_interval": self.input_poll_interval,
            "queue_timeout": self.queue_timeout
        }