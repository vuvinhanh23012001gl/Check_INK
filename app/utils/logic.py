import re
import numpy as np
import cv2


class Logic():
    @staticmethod
    def is_valid_id(id_value) -> bool:
        if id_value is None:
            return False
        id_str = str(id_value).strip()
        # Chỉ cho phép chữ số
        return bool(re.fullmatch(r"[0-9]+", id_str))
    
    async def convert_uploadfile_to_numpy(file) -> np.ndarray:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            print("Lỗi chuyển đổi UploadFile sang numpy ndarray")
            return None
        # cv2.imshow("anh show",img)
        return img
    
        
    @staticmethod
    def validate_full_regulation(data: dict) -> tuple[bool, str]:

        if not isinstance(data, dict):
            return False, "Data phải là dict"

        if "width" not in data or "heigh" not in data:
            return False, "Thiếu width hoặc heigh"

        if not isinstance(data["width"], int) or data["width"] <= 0:
            return False, "width phải là int > 0"

        if not isinstance(data["heigh"], int) or data["heigh"] <= 0:
            return False, "heigh phải là int > 0"

        width = data["width"]
        heigh = data["heigh"]

        color_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

        for key, value in data.items():

            if key in ("width", "heigh"):
                continue

            if not key.isdigit():
                return False, f"Key '{key}' không hợp lệ"

            if not isinstance(value, list):
                return False, f"Key '{key}' Không phải list"

            for idx, item in enumerate(value):

                if not isinstance(item, dict):
                    return False, f"{key}[{idx}] phải là dict"

                # ===== Bắt buộc phải có tọa độ =====
                for field in ["PointStarX","PointStarY","PointEndX","PointEndY"]:
                    if field not in item:
                        return False, f"{key}[{idx}] thiếu '{field}'"

                    if not isinstance(item[field], (int, float)):
                        return False, f"{key}[{idx}]['{field}'] phải là số"

                x1 = item["PointStarX"]
                y1 = item["PointStarY"]
                x2 = item["PointEndX"]
                y2 = item["PointEndY"]

                # ===== Boundary =====
                if not (0 <= x1 <= width and 0 <= x2 <= width):
                    return False, f"{key}[{idx}] X vượt boundary"

                if not (0 <= y1 <= heigh and 0 <= y2 <= heigh):
                    return False, f"{key}[{idx}] Y vượt boundary"

                # ===== Line length check =====
                if x1 == x2 and y1 == y2:
                    return False, f"{key}[{idx}] Line có độ dài = 0"

                # ===== Validate color =====
                color = item.get("color")
                if color is not None:
                    if not isinstance(color, str) or not color_pattern.match(color):
                        return False, f"{key}[{idx}] color không hợp lệ"

                # ===== Validate Level =====
                levels = []
                for i in range(1, 5):
                    level_key = f"level{i}"
                    value_level = item.get(level_key)

                    if value_level is None:
                        break

                    if not isinstance(value_level, (int, float)):
                        return False, f"{key}[{idx}]['{level_key}'] phải là số"

                    if value_level < 0:
                        return False, f"{key}[{idx}]['{level_key}'] không được âm"

                    levels.append(value_level)

                # phải có ít nhất 1 level
                if len(levels) == 0:
                    return False, f"{key}[{idx}] phải có ít nhất level1"

                # check tăng dần
                for i in range(1, len(levels)):
                    if levels[i] <= levels[i-1]:
                        return False, f"{key}[{idx}] Level phải tăng dần"

        return True, "Dữ liệu hợp lệ"

    def validate_calibration_data(data: dict):
        if not data:
            return {"status": False, "message": "Dữ liệu calibration rỗng"}

        # ===== name =====
        name = data.get("name")
        if not isinstance(name, str) or name.strip() == "":
            return {"status": False, "message": "Tên calibration không được để trống"}

        # ===== numberCapture =====
        number_capture = data.get("numberCapture")
        if not isinstance(number_capture, int) or number_capture <= 0:
            return {"status": False, "message": "Số lần chụp phải là số nguyên > 0"}

        if number_capture > 100:
            return {"status": False, "message": "Số lần chụp không được vượt quá 100"}

        # ===== reality =====
        reality = data.get("reality")
        if not isinstance(reality, (int, float)) or reality <= 0:
            return {"status": False, "message": "Chiều dài thực tế phải > 0"}

        # ===== tọa độ =====
        coords = [
            data.get("PointStarX"),
            data.get("PointStarY"),
            data.get("PointEndX"),
            data.get("PointEndY"),
        ]

        for v in coords:
            if not isinstance(v, (int, float)):
                return {"status": False, "message": "Tọa độ không hợp lệ"}

        # ===== kiểm tra trùng điểm =====
        if (
            data.get("PointStarX") == data.get("PointEndX")
            and data.get("PointStarY") == data.get("PointEndY")
        ):
            return {"status": False, "message": "Hai điểm calibration không được trùng nhau"}

        return {"status": True}