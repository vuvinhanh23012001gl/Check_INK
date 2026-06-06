import json
from pathlib import Path

class CalibrationReponsitory:
    def __init__(self, path_file):
        """
        Khởi tạo Repository quản lý file dữ liệu cấu hình các điểm (Points).
        Nếu file chưa tồn tại, tự động tạo file JSON rỗng ban đầu.
        """
        self.path_file = Path(path_file)
        self.path_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.path_file.exists():
            self.save_points({})

    def load_data(self) -> dict:
        """
        Chức năng: Đọc toàn bộ dữ liệu cấu hình từ file JSON.
        Input: None
        Output: dict -> Dữ liệu raw dạng dictionary đọc từ file, hoặc {} nếu file không tồn tại.
        """
        if not self.path_file.exists(): 
            return {}
            
        with open(self.path_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_data(self, data: dict) -> None:
        """
        Chức năng: Ghi đè cấu trúc dữ liệu dictionary hiện tại xuống file cấu hình JSON.
        Input: data (dict) -> Cấu trúc dữ liệu cần lưu trữ.
        Output: None
        """
        with open(self.path_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)