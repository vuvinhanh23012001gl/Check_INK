# import sys 
# from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parents[3]))

from app.utils import Folder
from app.config import PATH_PRODUCT_CHOOSE_PRODUCT

class ChooseProduct():
    def __init__(self,obj_folder:Folder):
          self.obj_folder = obj_folder
          self.name_choose_product = "product"  
          self.default_data_when_empyty = -1
          self.path_file_config =  PATH_PRODUCT_CHOOSE_PRODUCT
          self.choose = self.read_data_file_choose_product().get(self.name_choose_product,-1)
        
    def __repr__(self):
          return f"Sản phẩm đang được chọn là{self.name_choose_product} : {self.choose}"
    
    def get_choose_product_pick(self):
         return self.choose
         
    def set_choose_product(self,ID:int):
        if isinstance(ID,int):
            self.choose = ID 
            self.obj_folder.write_json_in_file(self.path_file_config,{f"{self.name_choose_product}":ID})
        else:
            print("Dữ liệu không hợp lệ, phải là dict")
            return False
        return True
    

    def read_data_file_choose_product(self):
        data  = self.obj_folder.read_json_from_file(self.path_file_config)
        if not data:
            send = {f"{self.name_choose_product}":self.default_data_when_empyty}
            self.obj_folder.write_json_in_file(self.path_file_config,send)
            self.choose = self.default_data_when_empyty
            return send
        else:
             return data
        

    def set_value_default(self):
        send = {f"{self.name_choose_product}":self.default_data_when_empyty}
        self.obj_folder.write_json_in_file(self.path_file_config,send)
        self.choose  = self.default_data_when_empyty

         
            



        
    

   
# p1 = ChooseProduct()
# print(p1.get_choose_product_pick())
# p1.set_value_default()
# print(p1.get_choose_product_pick())
# p1.set_choose_product(2)
# print(p1.get_choose_product_pick())
# p1.write_data_file_choose_product(1)
# print(p1.read_data_file_choose_product())