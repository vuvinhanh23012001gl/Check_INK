# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))
# from log_txt import Log_Txt
# from log_img  import Log_Img
# from log_csv import Log_CSV

import threading
import time
from datetime import datetime
from .config_software import Config_SoftWare   # class
from .log_txt import Log_Txt
from .log_img  import Log_Img
from .log_csv import Log_CSV
from app.services import ProductService,ChooseProductService
from queue import Queue
from app.utils import Folder,Aggregate

class Manager_Log:
    def __init__(self,obj_folder:Folder,Config_Software:Config_SoftWare,choose_product:ChooseProductService,product_service:ProductService,obj_aggregate:Aggregate,queue_manager_log:Queue):

        self.thread = None
        self.thread_running = None
        
        self.obj_aggregate = obj_aggregate
        self.obj_folder = obj_folder
        self.obj_Config_SoftWare = Config_Software
        self.obj_choose_product  = choose_product
        self.obj_product_service = product_service

        self.obj_Log_Txt  = None
        self.obj_Log_Img = None

        self.path_img = None
        self.path_csv = None
        self.path_txt = None
        self.queue_manager_log =  queue_manager_log
        self.Init()
    
    def Init(self):
        id_select =  self.obj_choose_product.get_choose_product()
        # print("id_select",id_select.data)
        name_product = self.obj_product_service.get_product_by_id(id_select.data)
        name_product_save_folder  = self.obj_aggregate.normalize_folder_name(name_product.data)
        # print("name_product",name_product.data.id)
        # print("name_product_save_folder",name_product_save_folder)
        data_dict_path = self.obj_Config_SoftWare.create_path_by_name_product(name_product_save_folder)
        self.path_img  = data_dict_path.get("path_log_img")
        self.path_txt  = data_dict_path.get("path_log_txt")
        self.path_csv = data_dict_path.get("path_log_csv")
        # print(self.path_img)

        open_log_txt = self.obj_Config_SoftWare.get_open_txt()
        open_log_console =  self.obj_Config_SoftWare.get_open_log_cosole()
        open_log_csv  = self.obj_Config_SoftWare.get_open_csv()
        open_log_img = self.obj_Config_SoftWare.get_open_img()

        self.obj_Log_Txt = Log_Txt(self.obj_folder,path_folder_log = self.path_txt ,enable_file = open_log_txt, enable_console = open_log_console)
        self.obj_Log_Img = Log_Img(self.obj_folder,path_img = self.path_img,open_log_img= open_log_img)
        self.obj_Log_Csv = Log_CSV(folder = self.path_csv,enable = open_log_csv,header=["product_id", "result", "score"])
    
        if any([open_log_txt]):
            self.start_thread()
        else:
            self.stop_log_thread()

    def start_thread(self):
        if not self.thread_running and not self.thread:
            self.thread_running = True
            self.thread = threading.Thread(target=self._log_thread_loop, daemon = True)
            self.thread.start()

    def _log_thread_loop(self):
        print("mở luồng nhận nhận dữ liệu log ảnh, img, csv")
        while self.thread_running:
            data = self.queue_manager_log.get()
            if data:
                type_data = data.get("type",None)
                msg =  data.get("msg",None)
                if type_data == "system":
                   level =  data.get("level","infor")
                   if level == "infor":
                       self.obj_Log_Txt.info(msg)
                   elif (level == "warning"):
                       self.obj_Log_Txt.warning(msg)
                   elif (level == "debug"):
                       self.obj_Log_Txt.debug(msg)
                   elif (level ==  "error"):
                       self.obj_Log_Txt.error(msg)
                   elif (level == "critical"):
                       self.obj_Log_Txt.critical(msg)
                elif type_data == "image":
                    now =  datetime.now()
                    file_name = f"img_{now.strftime('%y%m%d_%H%M%S')}_{now.microsecond // 1000:03d}"
                    self.obj_Log_Img.save(msg,file_name)  #msg  la img la anh 
                elif type_data == "csv":
                    # print(msg)
                    self.obj_Log_Csv.write(msg)  # msg la dict
            time.sleep(0.001)

    def stop_log_thread(self):
        """
        Dừng luồng ghi log an toàn.
        """
        self.thread_running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread =  None


#{"type":"system","level":"debug","msg":"xin chao ban nhe"}
#{"type":"image","msg":img} img la anh np
#{"type":"csv","msg":dict} dict data

# log_csv.write({
#     "product_id": 102,
#     "result": "NG",
#     "score": 0.45
# })



# c1 =  Config_SoftWare()
# choose1 = ChooseProduct()
# mana =  ProductManager()
# m1 = Manager_Log(c1,choose1,mana)


# while(True):
#     import time
#     data = {"type":"system","level":"debug","msg":"xin chao ban nhe"}
#     obj_queue.put(name_queue_manage,data)
#     # data1 = {"type":"image","level":"debug","msg":"xin chao ban nhe"}
#     # obj_queue.put(name_queue_manage,data1)
#     data_test =  {
#     "product_id": 102,
#     "result": "NG",
#     "score": 0.45
#     }
#     data2 = {"type":"csv","msg":data_test}
#     obj_queue.put(name_queue_manage,data2)    
#     time.sleep(1)

                
                    # from datetime import datetime
                    # import cv2
                    # import numpy as np
                    # # Tạo ảnh test (nền xám)
                    # img = np.full((480, 640, 3), 200, dtype=np.uint8)
                    # # Vẽ chữ TEST lên ảnh
                    # cv2.putText(
                    #     img,
                    #     "TEST IMAGE",
                    #     (150, 240),
                    #     cv2.FONT_HERSHEY_SIMPLEX,
                    #     1.2,
                    #     (0, 0, 255),
                    #     2,
                    #     cv2.LINE_AA
                    # )