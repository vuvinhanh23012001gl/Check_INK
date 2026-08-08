from app.core import Result, ErrorCode
from app.repository import JudmentLawProductRepository
class JudmentLawProductSevice:
    def __init__(self,repo:JudmentLawProductRepository):
        self.repo =  repo

    def save_data(self,data:dict,data_frame:dict):
        if self.compare_structure(data=data,data_frame=data_frame):
            print("So sánh thuộc cấu trúc cây tiến hành lưu")
            self.repo.update_data(data,False)
            return Result.Ok()
        else:
            return Result.Fail(ErrorCode.DATA_IS_NOT_CORRECT_FROMAT)

    def get_product_data(self, product_id: str) -> Result:
            """Lấy toàn bộ dữ liệu của một Product dựa trên product_id.
            Args:
                product_id: ID của sản phẩm cần lấy.
            Returns:
                Result: Chứa dict dữ liệu nếu tìm thấy, hoặc lỗi PRODUCT_NOT_FOUND.
            """
            product_data = self.repo.get_product(product_id)
            if not product_data:
                return Result.Fail(ErrorCode.PRODUCT_NOT_FOUND)
            return Result.Ok({
            str(product_id):product_data
        })

    def get_frame_data(self, product_id: str, frame_id: str) -> Result:
        """Lấy dữ liệu của một Frame cụ thể thuộc Product.
        
        Args:
            product_id: ID sản phẩm.
            frame_id: ID Frame cần lấy.
        Returns:
            Result: Chứa dict dữ liệu Frame hoặc lỗi tương ứng.
        """
        # Kiểm tra sản phẩm trước
        if not self.repo.get_product(product_id):
            return Result.Fail(ErrorCode.PRODUCT_NOT_FOUND)
        frame_data = self.repo.get_frame(product_id, frame_id)
        if not frame_data:
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
        return Result.Ok(frame_data)

    def get_item_data(self, product_id: str, frame_id: str, item_id: str) -> Result:
        """Lấy chi tiết dữ liệu của một Item cụ thể từ Product và Frame.
        
        Args:
            product_id: ID sản phẩm.
            frame_id: ID Frame.
            item_id: ID Item cần lấy.
        Returns:
            Result: Chứa dict dữ liệu Item hoặc lỗi nếu không tồn tại.
        """
        # Kiểm tra tuần tự từ gốc tới ngọn để trả về lỗi chính xác
        if not self.repo.get_product(product_id):
            return Result.Fail(ErrorCode.PRODUCT_NOT_FOUND)
        if not self.repo.get_frame(product_id, frame_id):
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
        item_data = self.repo.get(product_id, frame_id, item_id)
        if item_data is None:
            # Vì trong Enum chưa có ITEM_NOT_FOUND, sử dụng tạm DATA_INVALID
            return Result.Fail(ErrorCode.DATA_INVALID) 
        return Result.Ok(item_data)



    def compare_structure(self, data: dict, data_frame: dict) -> bool:
        """So sánh cấu trúc dict, cho phép data có nhiều key hơn.
        Args:
            data: Cấu trúc nguồn.
            data_frame: Cấu trúc cần so sánh.
        Returns:
            bool: True nếu data_frame là tập con của data.
        """
        for key, value in data_frame.items():
            if key not in data:
                return False
            if isinstance(value, dict):
                if not isinstance(data[key], dict):
                    return False
                if not self.compare_structure(data[key], value):
                    return False
        return True