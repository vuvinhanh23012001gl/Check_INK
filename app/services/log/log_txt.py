# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))

from app.utils import Folder
import logging

class Log_Txt:
    """
    Quản lý log của phần mềm:
    - Ghi log ra console
    - Ghi log ra file
    """
    def __init__(
        self,obj_folder:Folder,
        path_folder_log: str,
        name: str = "app",
        name_file: str = "system.txt",
        enable_console: bool = True,
        enable_file: bool = True,
    ):
        # Đảm bảo file log tồn tại
        self.obj_folder = obj_folder
        # Logger core
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.propagate = False

        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s]: %(message)s"
        )

        # Handler references
        self.handler_console: logging.StreamHandler | None = None
        self.handler_file: logging.FileHandler | None = None

        # Bật theo cấu hình
        if enable_file:
            self.path_log = self.obj_folder.ensure_file(path_folder_log, name_file)
            self.enable_file()

        if enable_console:
            self.enable_console()

    # ======================
    # Console log
    # ======================
    def enable_console(self):
        if self.handler_console is None:
            print("Bật log console")
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(self.formatter)
            self.logger.addHandler(ch)
            self.handler_console = ch

    def disable_console(self):
        if self.handler_console:
            print("Tắt log console")
            self.logger.removeHandler(self.handler_console)
            self.handler_console = None

    # ======================
    # File log
    # ======================
    def enable_file(self):
        if self.handler_file is None:
            print("Bật log file:", self.path_log)
            fh = logging.FileHandler(self.path_log, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.formatter)
            self.logger.addHandler(fh)
            self.handler_file = fh

    def disable_file(self):
        if self.handler_file:
            print("Tắt log file")
            self.logger.removeHandler(self.handler_file)
            self.handler_file.close()
            self.handler_file = None

    # ======================
    # Log API
    # ======================
    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)


# obj_log_txt = Log_Txt(
#     path_folder_log="C:\\App_Line_Measurement_Check\\Log\\date_21-01-2026\\log_systems",
#     enable_console=True,
#     enable_file=True
# )
# obj_log_txt.info("Test ghi log 1")
# obj_log_txt.error("Test lỗi")
