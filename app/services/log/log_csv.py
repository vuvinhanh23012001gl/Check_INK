import csv
from pathlib import Path
from datetime import datetime
import threading
class Log_CSV:
    def __init__(
        self,
        folder: str,
        filename: str = "log.csv",
        header: list[str] | None = None,
        enable: bool = True,
        auto_timestamp: bool = True,
        time_format: str = "%Y-%m-%d %H:%M:%S.%f",
    ):
        self.enable = enable
        self.auto_timestamp = auto_timestamp
        self.time_format = time_format
        self.lock = threading.Lock()

        self.path_folder = Path(folder)
        self.path_file = self.path_folder / filename

        self.header = header or []
        if self.auto_timestamp and "timestamp" not in self.header:
            self.header.insert(0, "timestamp")

        if self.enable:
            self._init_file()

    def _init_file(self):
        self.path_folder.mkdir(parents=True, exist_ok=True)
        if not self.path_file.exists():
            with open(self.path_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.header)

    # =========================
    # WRITE LIST (theo header)
    # =========================
    def write(self, data: dict):
        if not self.enable:
            return

        if self.auto_timestamp:
            data["timestamp"] = datetime.now().strftime(self.time_format)

        row = [data.get(col, "") for col in self.header]

        with self.lock:
            with open(self.path_file, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(row)



# log_csv = LogCSV(
#     folder="log/csv",
#     filename="result.csv",
#     header=["product_id", "result", "score"],
# )

# log_csv.write({
#     "product_id": 101,
#     "result": "OK",
#     "score": 0.98
# })

# log_csv.write({
#     "product_id": 102,
#     "result": "NG",
#     "score": 0.45
# })
