
class TypeProduct:
    def __init__(self, id: int, name: str, description: str = "",line_regulation :list =[],run_point:list=[]):
        self._id = id
        self._name = name
        self._description = description
        # metadata
        self.created_at = ""
        self.updated_at = ""
        # thư mục lưu ảnh của loại sản phẩm

        self._arr_line_regulation = line_regulation
        self._arr_run_point = run_point

    # -------- id --------


    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int)->bool:
        if isinstance(value, int) and value > 0:
            self._id = value
            return True
        return False

    # -------- name --------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.strip()


    # -------- description --------
    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value or ""
   



    # --- Property cho arr_line_regulation ---
    @property
    def arr_line_regulation(self):
        return self._arr_line_regulation

    @arr_line_regulation.setter
    def arr_line_regulation(self, value):
        if isinstance(value, dict):
            self._arr_line_regulation = value
        else:
            print(f"[Lỗi] arr_line_regulation phải là dict, không thể nhận: {type(value)}")
    # --- Property cho arr_run_point ---
    @property
    def arr_run_point(self):
        return self._arr_run_point

    @arr_run_point.setter
    def arr_run_point(self, value):
        if isinstance(value, dict):
            self._arr_run_point = value
        else:
            print(f"[Lỗi] arr_run_point phải là dict, không thể nhận: {type(value)}")

 
    
    # -------- helper --------
    def __repr__(self):
        return (
            f"TypeProduct("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"points={len(self.arr_run_point)}, "
            f"lines={len(self.arr_line_regulation)}, "
            f"created='{self.created_at}'"
            f")"
        )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            # Metadata - Đảm bảo là chuỗi để JSON không bị lỗi
            "created_at": str(self.created_at) if self.created_at else "",
            "updated_at": str(self.updated_at) if self.updated_at else "",
            # Các mảng dữ liệu cấu hình
            "regulation": self.arr_line_regulation,
            "run_point": self.arr_run_point,
        }

# type_product_example = TypeProduct(1, "Example", "This is an example type product")
# print(type_product_example)
