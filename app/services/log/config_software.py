# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Title      : Check OIL bivn / Module config software
# Description:  Module config software
# Author     : Vu Vinh Anh
# Email      : anh.vu@example.com
# Created    : 2025-06-30
# Version    : 0.1
# License    : MIT
# -----------------------------------------------------------------------------
# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))
# # import psutil
# # for p in psutil.disk_partitions():
# #     print(p.device, p.mountpoint)

from pathlib import Path
from datetime import datetime
from app.config import PATH_CONFIG_SOFTWARE 
from app.utils import Folder
from app.utils import Aggregate


class Config_SoftWare:

    """Quản lý cấu hình phần mềm & đường dẫn log"""

    # ====== TIME CONFIG ======
    SET_TIME_DEFAULT_SAVE_LOG_IMG = 30
    SET_TIME_DEFAULT_SAVE_LOG_TXT = 30
    SET_TIME_DEFAULT_SAVE_LOG_EXCELL = 30

    # ====== APP INFO ======
    NAME = "App_Line_Measurement_Check"

    # ====== FOLDER NAME ======
    NAME_FOLDER_LOG = "Log"
    NAME_FOLDER_LOG_TXT = "log_systems"
    NAME_FOLDER_LOG_CSV = "log_csv"
    NAME_FOLDER_LOG_IMG = "log_img"

    # ====== BASE PATH ======
    DISK_SAVE = Path("C:/")

    # ====== DATE ======
    DATE_NOW = datetime.now().strftime("%d-%m-%Y")

    # ====== PATH CONFIG ======
    DEFAULT_PRODUCT = "UNKNOWN_PRODUCT"
    PATH_FOLDER_LOG = DISK_SAVE / NAME / NAME_FOLDER_LOG/f"date_{DATE_NOW}"

    PATH_SAVE_FOLDER_LOG_IMG = PATH_FOLDER_LOG/ DEFAULT_PRODUCT / NAME_FOLDER_LOG_IMG
    PATH_SAVE_FOLDER_LOG_TXT = PATH_FOLDER_LOG / DEFAULT_PRODUCT /NAME_FOLDER_LOG_TXT
    PATH_SAVE_FOLDER_LOG_CSV = PATH_FOLDER_LOG / DEFAULT_PRODUCT/NAME_FOLDER_LOG_CSV

    
    def __init__(self,obj_folder:Folder,obj_aggregate:Aggregate):

        self.obj_aggregate = obj_aggregate
        self.obj_folder = obj_folder
        self.path_config_software = self.obj_folder.get_or_create_json_by_path(PATH_CONFIG_SOFTWARE)
        self.data_read_head_config = self.obj_folder.read_json_from_file(self.path_config_software) 
        self.path_file_config = self.path_config_software
        self.disk_select = self.data_read_head_config.get("disk_select",Config_SoftWare.DISK_SAVE)

        self.time_save_img = self.data_read_head_config.get("time_save_img",Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_IMG)
        self.time_save_txt =  self.data_read_head_config.get("time_save_txt",Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_TXT)
        self.time_save_csv =  self.data_read_head_config.get("time_save_csv",Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_EXCELL)

        self.open_img = self.data_read_head_config.get("open_img",True)
        self.open_txt =  self.data_read_head_config.get("open_txt",True)
        self.open_csv =  self.data_read_head_config.get("open_csv",True)
     
        self.open_log_print = self.data_read_head_config.get("open_log_print",True)
        self.open_log_cosole = self.data_read_head_config.get("open_log_cosole",True)
        
    def create_path_by_name_product(self, name_product):
        """
        Thay đổi đường dẫn log theo tên sản phẩm.
        - name_product phải là chuỗi và độ dài > 0
        - nếu không hợp lệ → trả về đường dẫn mặc định
        """

        default_path = {
            "path_log_txt": Config_SoftWare.PATH_SAVE_FOLDER_LOG_TXT,
            "path_log_csv": Config_SoftWare.PATH_SAVE_FOLDER_LOG_CSV,
            "path_log_img": Config_SoftWare.PATH_SAVE_FOLDER_LOG_IMG,
        }

        # Kiểm tra kiểu + độ dài chuỗi
        if not isinstance(name_product, str):
            return default_path

        name_product = name_product.strip()
        if len(name_product) == 0:
            return default_path

        path_img = (
            Config_SoftWare.PATH_FOLDER_LOG
            / name_product
            / Config_SoftWare.NAME_FOLDER_LOG_IMG
        )
        path_txt = (
            Config_SoftWare.PATH_FOLDER_LOG
            / name_product
            / Config_SoftWare.NAME_FOLDER_LOG_TXT
        )
        path_csv = (
            Config_SoftWare.PATH_FOLDER_LOG
            / name_product
            / Config_SoftWare.NAME_FOLDER_LOG_CSV
        )

        return {
            "path_log_txt": path_txt,
            "path_log_csv": path_csv,
            "path_log_img": path_img,
        }

        
    def to_dict(self):
        return {
            "time_save_img": self.time_save_img,
            "time_save_txt": self.time_save_txt,
            "time_save_csv": self.time_save_csv,

            "open_img": self.open_img,
            "open_txt": self.open_txt,
            "open_csv": self.open_csv,

            "open_log_print": self.open_log_print,
            "open_log_cosole": self.open_log_cosole,
          
        }
    

    def save_config_software(self):
        self.obj_folder.write_json_in_file(self.path_file_config,self.to_dict())
    

    def get_time_save_img(self):
        return self.time_save_img

    def set_time_save_img(self, value):
        try:
            value = int(value)
            if value <= 0:
                value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_IMG
        except:
            value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_IMG
        self.time_save_img = value


    def get_time_save_txt(self):
        return self.time_save_txt

    def set_time_save_txt(self, value):
        try:
            value = int(value)
            if value <= 0:
                value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_TXT
        except:
            value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_TXT
        self.time_save_txt = value


    def get_time_save_csv(self):
        return self.time_save_csv

    def set_time_save_csv(self, value):
        try:
            value = int(value)
            if value <= 0:
                value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_EXCELL
        except:
            value = Config_SoftWare.SET_TIME_DEFAULT_SAVE_LOG_EXCELL

        self.time_save_csv = value


    def get_disk_select(self):
        return self.disk_select

    def set_disk_select(self, value):
        try:
            self.disk_select = Path(value)
        except:
            self.disk_select = Config_SoftWare.PATH_SAVE_FOLDER_LOG_CSV


    def get_open_img(self):
        return self.open_img

    def set_open_img(self, value):
        self.open_img = bool(value)


    def get_open_csv(self):
        return self.open_csv

    def set_open_csv(self, value):
        self.open_csv = bool(value)

    def get_open_txt(self):
        return self.open_txt

    def set_open_txt(self, value):
        self.open_txt = bool(value)


    def get_open_log_print(self):
        return self.open_log_print

    def set_open_log_print(self, value):
        self.open_log_print = bool(value)

    def get_open_log_cosole(self):
        return self.open_log_cosole

    def set_open_log_cosole(self, value):
        self.open_log_cosole = bool(value)

    def get_arr_disk_on_pc(self):
        """Hàm trả về list rỗng nếu không"""
        return self.obj_folder.list_drives()
    

# c1 =  Config_SoftWare()
# # c1.save_config_software()
# # data  = c1.to_dict()
# # print(data)
# c1.save_config_software()
# print(Config_SoftWare.PATH_SAVE_FOLDER_LOG_IMG)
# print(Config_SoftWare.PATH_SAVE_FOLDER_LOG_TXT)
# print(Config_SoftWare.PATH_SAVE_FOLDER_LOG_CSV)
# # c1.create_location_save_log()



class Change_Disk:
    def __init__(self,obj_config_softWare:Config_SoftWare,obj_folder:Folder,obj_aggregate:Aggregate):
        self.obj_aggregate = obj_aggregate
        self.obj_folder = obj_folder
        self.obj_config_softWare = obj_config_softWare
    def arr_disk_on_pc(self):
        return self.obj_folder.list_drives()
    
    def found_currently_selecting(self,disk):
        """Kiểm tra ổ này có đang được chọn
        trả về 0 nếu tồn tại nhưng chưa được chọn
        trả về 1 nếu tồn tại và không được chọn
        trả vê -1 nếu không tồn tại
        """
        arr_disk = self.arr_disk_on_pc()
        if disk in arr_disk:
            print("Tìm thấy ổ")
            disk_current = self.obj_config_softWare.get_disk_select()
            if disk == disk_current:
                print("Ổ này đang được chọn")
                return 1,"Select"
            return 0,"DisSlect"
        else:
            print("Không tìm thấy ổ trong danh sách")
            return  -1,"FoundDisk"
        
    # def change_disk(self,disk):
    #     status,_  = self.found_currently_selecting(disk)
    #     if status == 1:
    #         return False,_
    #     elif status == 0:
    #         print("Thực hiện đổi đường dẫn ổ")
    #         path_img = self.obj_config_softWare.get_path_log_img()
    #         path_txt = self.obj_config_softWar.get_path_log_txt()
    #         path_csv = self.obj_config_softWar.get_path_log_csv()

    #         path_img_new = self.obj_aggregate.replace_drive(path_img,disk)
    #         path_txt_new = self.obj_aggregate.replace_drive(path_txt,disk)
    #         path_csv_new =  self.obj_aggregate.replace_drive(path_csv,disk)

    #         self.obj_config_softWare.set_path_log_csv(path_csv_new)
    #         self.obj_config_softWar.set_path_log_img(path_img_new)
    #         self.obj_config_softWar.set_path_log_txt(path_txt_new) 
    #         self.obj_config_softWar.disk_select =  disk
    #         self.obj_config_softWar.save_config_software()
    #         # Lam gi tiep o day dc roi do
    #         print("Đổi đường dẫn ổ thành công")
    #         return True,"OK"
    #     return False,_ 

    

        
 




# c2 = Change_Disk(c1)
# print(c2.change_disk("C:\\"))