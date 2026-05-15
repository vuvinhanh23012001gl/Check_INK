

import cv2
import numpy as np
import datetime
from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parents[3]))

from app.utils import Folder
from app.utils import Tool_OpenCv2
from app.config import PATH_PRODUCT_DATA, PATH_PRODUCT_IMG,PATH_PRODUCT_ROI_PRODUCT_IMG
from .product import TypeProduct

class ProductManager:

    ERRO_NOT_FOUND_ID ="ErroNotFound"
    ERRO_IMG_EMPTY = "ErroImgEmpty"
    ERRO_EMPTY_DATA = "ErroEmpytyData"
    ERRO_FAILD_SAVE  = "ErroFaildSave"
    SUCCESS = "Success"
    NAME_HEAD_IMG_FILE_ROI_PRODUCT = "coordinates"
    EXTENT_FILE_IMG_ROI_PRODUCT = "jpg"

    def __init__(self,obj_cv2:Tool_OpenCv2):

        self.obj_cv2 = obj_cv2
        self.name_manager = "type_products"
        self.path_file_config =  PATH_PRODUCT_DATA
        self.type_products = self.read_file_in_config() # Danh sách loại sản phẩm

    def add_product(self,product:TypeProduct,img:np.ndarray=None)->bool:
        print("---- Thêm sản phẩm mới----")
        if isinstance(product,TypeProduct):
            for tp in self.type_products:
                if tp.id == product.id:
                    print(f"Loại sản phẩm với id = {product.id} đã tồn tại. Không thêm được !")
                    print("----Hết add product ----")
                    return False,"ErrorIDExists"
            time_now =  datetime.datetime.now()
            product.created_at = str(time_now)  # Updat cung luc voi luc tao
            product.updated_at = str(time_now)  # Updat cung luc voi luc tao
            path_save_img = str(Path(PATH_PRODUCT_IMG)/f"{product.id}.jpg")
            if not isinstance(img, np.ndarray) or img is None:
                print("Dữ liệu ảnh không hợp lệ, phải là numpy ndarray")
                img_default = self.obj_cv2.create_black_image(1920,1200)
                self.obj_cv2.save_image(img_default,path_save_img)
            else:
                self.obj_cv2.save_image(img,path_save_img)
            path_folder_save_roi_img_product = str(Path(PATH_PRODUCT_ROI_PRODUCT_IMG)/f"{product.id}")
            Folder.get_or_create_folder(path_folder_save_roi_img_product)
            self.type_products.append(product)
            self.write_product_in_config()
            print("Thêm sản phẩm mới thành công")
            print("----Hết add product ----")
            return True,"success"
        print("Dữ liệu không hợp lệ, phải là TypeProduct")
        print("----Hết add product ----")
        return False,"ErrorDataIncorect"
    

    def get_path_file_config(self):
        return self.path_file_config
    
    
    def write_product_in_config(self):
        data = [prod.to_dict() for prod in self.type_products]
        self.write_file_config({self.name_manager:data})
        

    def read_file_in_config(self):
        """Hàm này đọc file và Init vào biến type_products"""
        data = self.read_file_config()
        if not data:

            return []
        arr_data = data.get(self.name_manager,[])
        arr_obj = []
        if arr_data:
            for item in arr_data:
                sp = TypeProduct(
                    id = item.get("id",0),
                    name = item.get("name",""),
                    description = item.get("description","")
                )
                sp.created_at = item.get("created_at",None)
                sp.updated_at = item.get("updated_at",None)
                sp.arr_line_regulation = item.get("regulation",None)
                sp.arr_run_point = item.get("run_point",None)
                arr_obj.append(sp)
        return arr_obj



    def write_file_config(self,data:dict):
        if isinstance(data,dict):
            Folder.write_json_in_file(self.path_file_config,data)
        else:
            print("Dữ liệu không hợp lệ, phải là dict")
            return False
        return True
    


    def read_file_config(self)->dict:
        return Folder.read_json_from_file(self.path_file_config)
    

    def delete_product_by_id(self, product_id: int) -> bool:
        print("--- Xóa hết dữ liệu sản phẩm --")
        product_find = self.get_product_by_id(product_id)
        if not product_find:
            print(f"Không tìm thấy ID")
            print("---Hết xóa sản phầm  0% ----")
            return False
        for i, tp in enumerate(self.type_products):
            if product_id == tp.id:
                path_save_img = str(Path(PATH_PRODUCT_IMG)/f"{tp.id}.jpg")
                self.obj_cv2.delete_image(path_save_img)
                print(f"1.Đã xóa ảnh sản phẩm tại: {path_save_img}")
                self.type_products.pop(i)
                self.write_product_in_config()
                print(f"2.Đã data xóa sản phẩm với id={product_id}.")
                path_folder_roi_product = Path(PATH_PRODUCT_ROI_PRODUCT_IMG) / f"{tp.id}"
                Folder.delete_folder(path_folder_roi_product)
                print(f"3.Xóa thành công folder danh sách các ảnh ROI.")
                print("-- Hết xóa dữ liệu ---")
                return True,ProductManager.SUCCESS
        print(f"Không tìm thấy sản phẩm với id={product_id} để xóa.")
        print("-- Chưa xóa dữ liệu ---")
        return False,ProductManager.ERRO_NOT_FOUND_ID
        

    

    def get_to_dict_arr_path_src(self):
        """Trả về mảng dict của tất cả sản phẩm"""
        arr_dict_inf_product = []
        for prod in self.type_products:
            dict_out = prod.to_dict()
            path_save_img = str(Path(PATH_PRODUCT_IMG)/f"{prod.id}.jpg")
            path_poxis = Folder.get_parts_from_bottom(path_save_img,levels=3)
            dict_out["image_src"] =  str(path_poxis)
            arr_dict_inf_product.append(dict_out)
        return arr_dict_inf_product
    

    def get_product_by_id(self, product_id: int):
        """Nhập id → trả về object TypeProduct hoặc None"""
        for tp in self.type_products:
            if tp.id == product_id:
                return tp
        return None
    

    def get_product_name_by_id(self, product_id: int):
        """Nhập id → trả về tên sản phẩm hoặc None"""
        prod = self.get_product_by_id(product_id)
        if prod:
            return prod.name
        return None
    
    def add_point_img_product(self, id, img=None):
            print(f"------------Thêm ảnh tại id : {id}-------------")
            product_find = self.get_product_by_id(id)
            if not product_find:
                print(f"Không tìm thấy ID")
                print("---Hết thêm ảnh----")
                return False, ProductManager.ERRO_NOT_FOUND_ID
            if img is None:
                print(f"Ảnh trống img none")
                print("---Hết thêm ảnh----")
                return False, ProductManager.ERRO_IMG_EMPTY
            path_folder_roi_product = Path(PATH_PRODUCT_ROI_PRODUCT_IMG) / f"{id}"
            path_folder_roi_product.mkdir(parents=True, exist_ok=True) 
            list_name_file = Folder.get_list_files(path_folder_roi_product)
            # 3. Tìm index lớn nhất hiện có
            max_index = -1
            if len(list_name_file) != 0:
                for file_name in list_name_file:
                    try:
                        if file_name.startswith(ProductManager.NAME_HEAD_IMG_FILE_ROI_PRODUCT) and file_name.endswith(ProductManager.EXTENT_FILE_IMG_ROI_PRODUCT):
                            index_part = file_name.replace(f"{ProductManager.NAME_HEAD_IMG_FILE_ROI_PRODUCT}_", "").split('.')[0]
                            current_index = int(index_part)
                            if current_index > max_index:
                                max_index = current_index
                    except (ValueError, IndexError):
                        continue
            # 4. Tạo index mới và lưu file
            new_index = max_index + 1
            new_file_name = f"{ProductManager.NAME_HEAD_IMG_FILE_ROI_PRODUCT}_{new_index}.{ProductManager.EXTENT_FILE_IMG_ROI_PRODUCT}"
            path_file = path_folder_roi_product / new_file_name
            # Lưu ảnh bằng OpenCV
            success = cv2.imwrite(str(path_file), img)
            if success:
                print(f"Lưu ảnh thành công tại index {new_index}: {path_file.name}")
                print("---Hết thêm ảnh----")
                return True, ProductManager.SUCCESS
            else:
                print(f"Lỗi: Không thể ghi file tại {path_file}")
                print("---Hết thêm ảnh----")
                return False, ProductManager.ERRO_FAILD_SAVE


    def get_arr_path_img_roi_product_by_id(self, product_id: int):
        """Nhập id → trả về mảng đường dẫn ảnh ROI của sản phẩm hoặc None"""
        print("---- Vào hàm Lấy danh sách ảnh ROI của sản phẩm ---")
        product_find = self.get_product_by_id(product_id)
        if not product_find:
            print(f"Không tìm thấy ID")
            print("---- Hết hàm lấy sản danh sách ảnh sp ---")
            return False, ProductManager.ERRO_NOT_FOUND_ID
        path_folder_roi_product = Path(PATH_PRODUCT_ROI_PRODUCT_IMG) / f"{product_id}"
        list_name_file = Folder.get_list_files(path_folder_roi_product)
        if len(list_name_file) == 0:
            print(f"Chưa có ảnh ROI cho sản phẩm id={product_id}")
            print("---- Hết hàm lấy sản danh sách ảnh sp ---")
            return True, []
        arr_path_img_roi = []
        for file_name in list_name_file:
            full_path = path_folder_roi_product / file_name
            path_poxis = Folder.get_parts_from_bottom(full_path,levels=4)
            arr_path_img_roi.append(str(path_poxis))
        print("danh sách ảnh ROI:", arr_path_img_roi)
        print("---- Hết hàm lấy sản danh sách ảnh sp ---")
        return True, arr_path_img_roi
   
    def get_arr_data_run_point_product_by_id(self, product_id: int):
        # Ham nay để giả định dữ liệu 
        return [{    # Du lieu nay se la muon tam
                "x": 36,
                "y": 40,
                "brightness": 78
            }]
    
    def get_infor_product(self, product_id: int):
        # Ham nay để giả định dữ liệu 
        return  {
                "id": 1,
                "name":"Xin chao",
                "xyz": [1,2,4],
            }
            
    def get_data_regulation_by_product_id(self, product_id: int):
        print("---- Vào hàm Lấy dữ liệu vẽ draw ---")

        product = self.get_product_by_id(product_id)
        if not product:
            print("Không tìm thấy ID")
            print("---- Hết hàm lấy dữ liệu ảnh sp ---")
            return False, None, 0, ProductManager.ERRO_NOT_FOUND_ID

        regulation = product.arr_line_regulation

        if not isinstance(regulation, dict):
            return True, regulation, 0, ProductManager.SUCCESS

        # Đếm số group có key là số
        count = 0
        for key, value in regulation.items():
            if key.isdigit() and isinstance(value, list):
                count += 1

        print(f"Số group regulation: {count}")
        print("---- Hết hàm lấy dữ liệu ảnh sp ---")

        return True, regulation, count, ProductManager.SUCCESS

    def set_data_regulation_by_product_id(self, product_id: int, arr_regulation):
        print("---- Vào hàm SET dữ liệu vẽ draw ---")
        product_find = self.get_product_by_id(product_id)
        if not product_find:
            print("Không tìm thấy ID")
            print("---- Hết hàm SET dữ liệu ảnh sp ---")
            return False, ProductManager.ERRO_NOT_FOUND_ID

        if arr_regulation is None:
            print("Dữ liệu regulation rỗng")
            print("---- Hết hàm SET dữ liệu ảnh sp ---")
            return False, ProductManager.ERRO_EMPTY_DATA

        # Cập nhật dữ liệu
        product_find.arr_line_regulation = arr_regulation

        # Update thời gian
        product_find.updated_at = str(datetime.datetime.now())

        # Ghi lại vào file config
        self.write_product_in_config()

        print("Cập nhật regulation thành công")
        print("---- Hết hàm SET dữ liệu ảnh sp ---")

        return True, ProductManager.SUCCESS











# if __name__ == "__main__":
#     test = ProductManager()
# # #     test.delete_product_by_id(2)
# #     # test.get_path_file_config()
# #     # test.write_file_config({"name":"test","value":123})
# #     # print(test.read_file_config())
# #     # sp1 = TypeProduct(2,"Ao thun","Ao thun co co")
# #     # test.add_product(sp1)
# #     # img_default = obj_cv2.create_black_image(1920,1200)
# #     # test.add_point_img_product(1,img_default)
# #     # test.delete_product_by_id(1)
# #     # print(test.get_to_dict_arr_path_src())
# #     # test.write_product_in_config()
# #     # test.read_file_in_config()
# #     # test.get_arr_path_img_roi_product_by_id(1)


#     data_regulation = test.get_data_regulation_by_product_id(1)
#     print(data_regulation)

# #     # data_set_regulation = test.set_data_regulation_by_product_id(1,[323,3232,323,232,3232])
# #     # print(data_set_regulation)


    

    