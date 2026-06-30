import json
from pathlib import Path
from app.config import PATH_FILE_DATA_CONFIG_COM
class ComRepository:
    def __init__(self):
        self.path_file = Path(
            PATH_FILE_DATA_CONFIG_COM
        )
        self.path_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        # =====================
        # CREATE FILE
        # =====================
        if not self.path_file.exists():

            self.save_config({})

    # =========================
    # LOAD CONFIG
    # =========================
    def load_config(
        self
    ) -> dict:

        if not self.path_file.exists():

            return {}

        try:

            with open(
                self.path_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception:

            return {}

    # =========================
    # SAVE CONFIG
    # =========================

    def save_config(
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

    # =========================
    # UPDATE CONFIG
    # =========================

    def update_config(
        self,
        key,
        value
    ):

        data = self.load_config()

        data[key] = value

        self.save_config(data)

    # =========================
    # GET VALUE
    # =========================

    def get_value(
        self,
        key,
        default=None
    ):

        data = self.load_config()

        return data.get(
            key,
            default
        )

    # =========================
    # CLEAR CONFIG
    # =========================

    def clear_config(
        self
    ):

        self.save_config({})