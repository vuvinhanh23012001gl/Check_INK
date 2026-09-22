from app.core import Result, ErrorCode
from app.repository import JudmentLawProductRepository
from pathlib import Path
import copy
import cv2
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

    def convert_canvas_coordinates(
        self,
        data: dict,
        product_id: int,
        point_service,
        canvas_width: int,
        canvas_height: int,
    ) -> Result:
        """Chuyển tọa độ mọi inspector từ canvas sang pixel ảnh master.

        Input: ``data`` là cây judgment từ client; ``product_id`` là sản phẩm
            hiện tại; ``point_service`` dùng để lấy ảnh master; canvas có kích
            thước ``canvas_width`` x ``canvas_height``.
        Output: ``Result.Ok`` chứa bản sao dữ liệu đã chuyển đổi và đánh dấu
            ``coordinateSpace: image`` cho các inspector có tọa độ.
        Errors: ``Result.Fail`` nếu canvas không hợp lệ, thiếu ảnh master hoặc
            dữ liệu inspector hoặc tọa độ không đúng cấu trúc.
        """
        if canvas_width <= 0 or canvas_height <= 0:
            return Result.Fail(ErrorCode.INVALID_INPUT)
        converted = copy.deepcopy(data)
        product_data = converted.get(str(product_id), converted.get(product_id))
        if not isinstance(product_data, dict):
            return Result.Fail(ErrorCode.DATA_INVALID)
        for frame_id, frame_data in product_data.items():
            if not isinstance(frame_data, dict):
                continue
            for point_id, item_data in frame_data.items():
                if not isinstance(item_data, dict):
                    continue
                image_result = point_service.get_path_img_point(
                    int(product_id), int(frame_id), int(point_id)
                )
                if not image_result.ok:
                    return Result.Fail(ErrorCode.IMAGE_NOT_FOUND)
                image = cv2.imread(str(image_result.data))
                if image is None:
                    return Result.Fail(ErrorCode.IMAGE_NOT_FOUND)
                image_height, image_width = image.shape[:2]
                scale_x = image_width / canvas_width
                scale_y = image_height / canvas_height
                for inspector in item_data.values():
                    if not isinstance(inspector, dict):
                        continue
                    coordinate_items = (
                        inspector.values()
                        if self._is_collection_inspector(inspector)
                        else (inspector,)
                    )
                    for coordinate_item in coordinate_items:
                        if not isinstance(coordinate_item, dict):
                            return Result.Fail(ErrorCode.DATA_INVALID)
                        if coordinate_item.get("coordinateSpace") == "image":
                            continue
                        if not all(
                            key in coordinate_item
                            for key in ("xStart", "yStart", "xEnd", "yEnd")
                        ):
                            continue
                        try:
                            coordinate_item["xStart"] = int(
                                round(float(coordinate_item["xStart"]) * scale_x)
                            )
                            coordinate_item["yStart"] = int(
                                round(float(coordinate_item["yStart"]) * scale_y)
                            )
                            coordinate_item["xEnd"] = int(
                                round(float(coordinate_item["xEnd"]) * scale_x)
                            )
                            coordinate_item["yEnd"] = int(
                                round(float(coordinate_item["yEnd"]) * scale_y)
                            )
                        except (TypeError, ValueError):
                            return Result.Fail(ErrorCode.DATA_INVALID)
                        coordinate_item["coordinateSpace"] = "image"
        return Result.Ok(converted)

    def convert_canvas_border_coordinates(
        self,
        data: dict,
        product_id: int,
        point_service,
        canvas_width: int,
        canvas_height: int,
    ) -> Result:
        """Tên tương thích cũ của ``convert_canvas_coordinates``.

        Input, output và lỗi: Giống ``convert_canvas_coordinates``.
        """
        return self.convert_canvas_coordinates(
            data,
            product_id,
            point_service,
            canvas_width,
            canvas_height,
        )

    @staticmethod
    def _is_collection_inspector(inspector: dict) -> bool:
        """Xác định inspector chứa nhiều line/rectangle con.

        Input: Dict cấu hình của một inspector.
        Output: ``True`` nếu các value là các dict tọa độ con.
        Errors: Không phát sinh.
        """
        coordinate_keys = {"xStart", "yStart", "xEnd", "yEnd"}
        return not coordinate_keys.issubset(inspector)

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