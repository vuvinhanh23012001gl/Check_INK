from app.core import Result, ErrorCode
from app.model import Calibration  
from app.services import PointService
from app.repository import CalibrationReponsitory 
import statistics
from typing import List
from app.config import CalibrationConfig
class CalibrationService:
    def __init__(self, point_service: PointService, repository: CalibrationReponsitory):
        """
        Khởi tạo dịch vụ quản lý thông số Calibration cho từng Frame.
    
        :param point_service: Instance của PointService gốc để kiểm tra tính hợp lệ của ID.
        :param repository: Instance của CalibrationRepository để xử lý đọc/ghi file.
        """
        self.point_service = point_service
        self.repository = repository
        
        # Nạp toàn bộ dữ liệu từ Repository lên bộ nhớ RAM khi khởi tạo
        self.calibrations = self._init_calibrations_from_repo()

    def _init_calibrations_from_repo(self) -> dict:
        """Chuyển đổi dữ liệu thô (dict) từ Repository sang Object định dạng trong RAM"""
        raw_data = self.repository.load_data()
        calibrations = {}
        
        if not isinstance(raw_data, dict): 
            return {}

        for p_id, frame_dict in raw_data.items():
            if not isinstance(frame_dict, dict): 
                continue
            calibrations[p_id] = {}
            for f_id, calib_dict in frame_dict.items():
                if not isinstance(calib_dict, dict): 
                    continue
                calibrations[p_id][f_id] = Calibration.from_dict(calib_dict)
        return calibrations


    def _sync_to_repository(self) -> None:
        """Helper nội bộ: Chuyển đổi ngược dữ liệu RAM thành dict và đẩy xuống Repository lưu trữ"""
        data_to_save = {}
        for p_id, frame_dict in self.calibrations.items():
            data_to_save[p_id] = {}
            for f_id, calib_obj in frame_dict.items():
                data_to_save[p_id][f_id] = calib_obj.to_dict()
                
        # Gọi tầng Repository thực hiện ghi file
        self.repository.save_data(data_to_save)

    def get_calibration(self, product_id: int, frame_id: int) -> Result:
            """
            Chức năng: Lấy đối tượng Calibration của một Frame.
            """
            p_id_str, f_id_str = str(product_id), str(frame_id)
            
            # 1. Xác thực ID hệ thống có hợp lệ không
            id_tree = self.point_service.get_product_frame_id_tree()
            if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
                return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
                
            # 2. Kiểm tra tồn tại trong RAM (tận dụng hàm is_calibration_exists có sẵn)
            if not self.is_calibration_exists(product_id, frame_id):
                return Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND)
                
            # 3. Trả về đối tượng Calibration chuẩn
            calib = self.calibrations[p_id_str][f_id_str]
            return Result.Ok(calib)
    

    def get_calibration_dict_by_product(self, product_id: int) -> Result:
            """
            Chức năng: Lấy toàn bộ cấu hình Calibration của một Product dưới dạng Dictionary (JSON).
            Dữ liệu trả về bao gồm cả Product ID bọc ở ngoài cùng.
            Input: product_id (int)
            Output: 
                - Result.Ok(dict) dạng: {"1": {"0": {...}, "1": {...}}}
                - Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND) nếu không tìm thấy dữ liệu.
            """
            p_id_str = str(product_id)
            
            # 1. Kiểm tra xem dữ liệu Product này có tồn tại trong bộ nhớ RAM hay chưa
            if p_id_str not in self.calibrations:
                return Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND)
                
            # 2. Xác thực thêm với ID hệ thống từ PointService
            id_tree = self.point_service.get_product_frame_id_tree()
            if p_id_str not in id_tree:
                return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
                
            # 3. Tiến hành chuyển đổi toàn bộ các Frame của Product này sang dạng Dict
            frames_data = {}
            for f_id_str, calib_obj in self.calibrations[p_id_str].items():
                frames_data[f_id_str] = calib_obj.to_dict()
                
            # 4. Bọc lại bằng Product ID ở ngoài cùng theo đúng cấu trúc yêu cầu
            result_data = {
                p_id_str: frames_data
            }
                
            return Result.Ok(result_data)

    def add_calibration(self, product_id: int, frame_id: int, calibration: Calibration) -> Result:
            """
            Chức năng: Tạo mới hoàn toàn cấu hình Calibration cho một Frame từ một đối tượng Calibration có sẵn.
            """
            p_id_str, f_id_str = str(product_id), str(frame_id)
            
            # 1. Xác thực cấu trúc ID hệ thống hợp lệ
            id_tree = self.point_service.get_product_frame_id_tree()
            print("id_tree",id_tree)
            if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
                return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
                
            # 2. Cập nhật dữ liệu vào RAM và lưu trữ trực tiếp
            if p_id_str not in self.calibrations:
                self.calibrations[p_id_str] = {}
                
            # Gán trực tiếp đối tượng calibration nhận từ tham số vào RAM
            self.calibrations[p_id_str][f_id_str] = calibration
            self._sync_to_repository()
                
            return Result.Ok(self.calibrations[p_id_str][f_id_str])


    def delete_calibration(self, product_id: int, frame_id: int) -> Result:
        """
        Chức năng: Xóa bỏ thông số cấu hình Calibration của Frame và dọn dẹp node cha trống.
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        # 1. Kiểm tra tồn tại bản ghi trong RAM
        if p_id_str not in self.calibrations or f_id_str not in self.calibrations[p_id_str]:
            return Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND)
        calib_deleted = self.calibrations[p_id_str][f_id_str]
        # 2. Xóa node Frame khỏi RAM
        del self.calibrations[p_id_str][f_id_str]
        # 3. Dọn dẹp dứt điểm node Product trống nếu không còn frame nào
        if not self.calibrations[p_id_str]:
            del self.calibrations[p_id_str]
        # 4. Đồng bộ trạng thái mới sau khi xóa xuống Repository
        self._sync_to_repository()
        return Result.Ok(calib_deleted)
    


    def is_calibration_exists(self, product_id: int, frame_id: int) -> bool:
        """
        Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame 
                   có tồn tại trong RAM hay không.
        Input: product_id (int), frame_id (int)
        Output: bool -> True nếu đã cấu hình, False nếu chưa có dữ liệu.
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        return p_id_str in self.calibrations and f_id_str in self.calibrations[p_id_str]
    
    def is_calibration_exists_check_system(self, product_id: int, frame_id: int) -> bool:
        """
        Chức năng: Kiểm tra xem thông số cấu hình Calibration của một Frame có hợp lệ trên hệ thống
                   và đã tồn tại sẵn trong bộ nhớ RAM hay chưa.
        Input: product_id (int), frame_id (int)
        Output: bool -> True nếu ID hợp lệ VÀ đã được cấu hình, ngược lại trả về False.
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        
        # 1. Kiểm tra tính hợp lệ của ID từ PointService (Cây ID hệ thống)
        id_tree = self.point_service.get_product_frame_id_tree()
        if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
            return False
            
        # 2. Kiểm tra xem cặp ID đó đã được cấu hình đối tượng Calibration trong RAM chưa
        return p_id_str in self.calibrations and f_id_str in self.calibrations[p_id_str]
    
    def is_frame_exists_in_system(self, product_id: int, frame_id: int) -> bool:
            """
            Chức năng: Kiểm tra xem cặp product_id và frame_id có tồn tại trong hệ thống (ID Tree) hay không.
            Input: product_id (int), frame_id (int)
            Output: bool -> True nếu ID hợp lệ và tồn tại trên hệ thống, ngược lại trả về False.
            """
            p_id_str, f_id_str = str(product_id), str(frame_id)
            
            # 1. Lấy cây ID cấu hình hiện tại của hệ thống từ PointService
            id_tree = self.point_service.get_product_frame_id_tree()
            
            # 2. Kiểm tra xem Product ID và Frame ID có nằm trong cây dữ liệu không
            if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
                return False
                
            return True

    def delete_calibration(self, product_id: int, frame_id: int) -> Result:
            """
            Chức năng: Xóa bỏ thông số cấu hình Calibration của một Frame dựa vào product_id và frame_id.
                    Đồng thời dọn dẹp node cha (Product) nếu không còn frame nào bên trong.
            Input:
                - product_id (int)
                - frame_id (int)
            Output:
                - Result.Ok(calib_deleted) nếu xóa thành công.
                - Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND) nếu không tìm thấy bản ghi.
            """
            p_id_str, f_id_str = str(product_id), str(frame_id)

            # 1. Kiểm tra tồn tại bản ghi trong RAM
            if not self.is_calibration_exists(product_id, frame_id):
                return Result.Fail(ErrorCode.CALIBRATION_NOT_FOUND)

            # 2. Lấy đối tượng ra để trả về trước khi xóa khỏi bộ nhớ
            calib_deleted = self.calibrations[p_id_str][f_id_str]

            # 3. Thực hiện xóa node Frame khỏi RAM
            del self.calibrations[p_id_str][f_id_str]

            # 4. Dọn dẹp dứt điểm node Product trống nếu không còn frame nào bên trong
            if not self.calibrations[p_id_str]:
                del self.calibrations[p_id_str]

            # 5. Đồng bộ trạng thái dữ liệu mới sau khi xóa xuống tầng Repository (File cứng)
            self._sync_to_repository()

            return Result.Ok(calib_deleted)
    





    @staticmethod
    def calculate_calibration_metrics(
        pixel_list: List[float], 
        reality_length: float, 
        z_thresh: float = 3.5
    ) -> Result:
        """
        Logic core xử lý toán học và lọc nhiễu MAD thuần túy.
        Không phụ thuộc vào ID hệ thống hay tầng lưu trữ dữ liệu.
        Trả về:
            - Result.Ok(metrics_dict) nếu tính toán thành công.
            - Result.Fail(ErrorCode) nếu dữ liệu đầu vào hoặc kết quả lọc không hợp lệ.
        """
        # 1. Kiểm tra dữ liệu đầu vào cơ bản
        if not pixel_list:
            return Result.Fail(ErrorCode.CALIBRATION_EMPTY_DATA)
        if len(pixel_list) < CalibrationConfig.MIN_NUMBER_CALIBRATION_METRICS:
            return Result.Fail(ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE)
        if len(pixel_list) > CalibrationConfig.MAX_NUMBER_CALIBRATION_METRICS:
            return Result.Fail(ErrorCode.CALIBRATION_NOT_ENOUGH_SAMPLE)
        if reality_length <= 0:
            return Result.Fail(ErrorCode.CALIBRATION_INVALID_REAL_LENGTH)


        median_pixel = statistics.median(pixel_list)
        abs_devs = [abs(x - median_pixel) for x in pixel_list]
        mad = statistics.median(abs_devs)

        if mad == 0:
            filtered = pixel_list
        else:
            filtered = []
            for x in pixel_list:
                # Modified Z-score chuẩn hóa theo phân phối Gaussian
                z_score = 0.6745 * (x - median_pixel) / mad
                if abs(z_score) <= z_thresh:
                    filtered.append(x)

        # Kiểm tra xem sau khi lọc còn đủ số mẫu tối thiểu không
        if len(filtered) < 3:
            return Result.Fail(ErrorCode.CALIBRATION_FILTERED_TOO_MUCH)
            
        # 3. Tính toán các thông số thống kê toán học
        pixel_mean = statistics.mean(filtered)
        
        if pixel_mean == 0:
            return Result.Fail(ErrorCode.CALIBRATION_INVALID_MEAN)
            
        pixel_std = statistics.stdev(filtered)
        scale = reality_length / pixel_mean
        scale_error = scale * (pixel_std / pixel_mean)
        cv = pixel_std / pixel_mean

        # Tính toán mức độ tin cậy (Confidence score) kết hợp tỷ lệ giữ lại mẫu sạch
        retention_rate = len(filtered) / len(pixel_list)
        confidence = max(0.0, min(1.0, 1.0 - cv))
        confidence *= retention_rate

        # 4. Gom toàn bộ kết quả tính toán thành một cấu trúc dữ liệu phẳng
        metrics = {
            "reality_mm": reality_length,
            "pixel_mean": pixel_mean,
            "pixel_std": pixel_std,
            "cv": cv,
            "scale_mm_per_pixel": scale,
            "scale_error_mm_per_pixel": scale_error,
            "confidence": confidence,
            "samples_used": len(filtered),
            "samples_raw": len(pixel_list),
            "mad": mad
        }
        return Result.Ok(metrics)
    


    @staticmethod
    def analyze_data_to_arrays(data_dict):
        """
        Hàm phân tích cấu trúc dữ liệu JSON lồng nhau thành một mảng phẳng (flat array) duy nhất.
        """
        flat_elements = []  # Mảng duy nhất chứa toàn bộ thông tin đã làm phẳng
        # Duyệt qua từng Product ID
        for prod_id, frames in data_dict.items():
            # Duyệt qua từng Frame ID trong Product đó
            for frame_id, frame_content in frames.items():
                # Lấy dict calculation_parameters bên trong ra
                params = frame_content.get('calculation_parameters', {})
                if not params:
                    continue
                    
                # Tạo một dictionary phẳng chứa toàn bộ thông tin của item
                item_flat = {
                    'product_id': prod_id,
                    'frame_id': frame_id,
                    'lineName': params.get('lineName'),
                    'realityMM': float(params.get('realityMM', 0)),     # Ép kiểu về số thực
                    'captureCount': int(params.get('captureCount', 0)), # Ép kiểu về số nguyên
                    'id_item': params.get('id_item'),
                    
                    # Gom các tọa độ 2D (Start / End) vào chung
                    'xStart': params.get('xStart'),
                    'yStart': params.get('yStart'),
                    'xEnd': params.get('xEnd'),
                    'yEnd': params.get('yEnd'),
                    
                    # Gom các tọa độ không gian 3D vào chung luôn
                    'coordinateX': params.get('coordinateX'),
                    'coordinateY': params.get('coordinateY'),
                    'coordinateZ': params.get('coordinateZ')
                }
                # Thêm item đã làm phẳng vào mảng tổng
                flat_elements.append(item_flat)
        return flat_elements
    

    def check_calibration_data(
            self, 
            product_id: str, 
            frame_id: str, 
            id_tems: str, 
            number_capture: int, 
            reality_mm: float,
            startX: int,
            startY: int,
            endX: int,
            endY: int
        ) -> bool:
            """
            Kiểm tra trùng khớp tất cả dữ liệu cấu hình bao gồm cả tọa độ vùng chọn (startX, startY, endX, endY).
            In rõ chi tiết giá trị trước (hiện tại trong hệ thống) và giá trị sau (truyền vào kiểm tra).
            """
            # 1. Ép kiểu dữ liệu đầu vào để đồng bộ so sánh
            p_id = str(product_id)
            f_id = str(frame_id)
            t_id = str(id_tems)
            n_cap = int(number_capture)
            r_mm = float(reality_mm)
            s_X = int(startX)
            s_Y = int(startY)
            e_X = int(endX)
            e_Y = int(endY)

            # 2. Kiểm tra xem product_id và frame_id có tồn tại không
            if p_id not in self.calibrations or f_id not in self.calibrations[p_id]:
                print(f"[-] Không tìm thấy product_id: {p_id} hoặc frame_id: {f_id} trong hệ thống.")
                return False
            
            # 3. Lấy đối tượng Calibration hiện tại ra
            calibration_obj = self.calibrations[p_id][f_id]
            
            # Lấy các giá trị hiện tại (Trước)
            curr_id_tems = str(calibration_obj.id_tems)
            curr_number_capture = int(calibration_obj.number_capture)
            curr_reality_mm = float(calibration_obj.reality_mm)
            curr_startX = int(calibration_obj.startX)
            curr_startY = int(calibration_obj.startY)
            curr_endX = int(calibration_obj.endX)
            curr_endY = int(calibration_obj.endY)

            # 4. In log so sánh chi tiết (Giá trị TRƯỚC vs Giá trị SAU)
            print("\n" + "="*60)
            print(f"KIỂM TRA SO SÁNH CALIBRATION ĐẦY ĐỦ [Product: {p_id} | Frame: {f_id}]")
            print("-"*60)
            
            # Kiểm tra các thông số cơ bản
            match_id = curr_id_tems == t_id
            print(f"-> id_tems:       [Trước] '{curr_id_tems}' {'==' if match_id else '!='} [Sau] '{t_id}'")
            
            match_capture = curr_number_capture == n_cap
            print(f"-> number_capture:[Trước] {curr_number_capture} {'==' if match_capture else '!='} [Sau] {n_cap}")
            
            match_reality = curr_reality_mm == r_mm
            print(f"-> reality_mm:    [Trước] {curr_reality_mm} {'==' if match_reality else '!='} [Sau] {r_mm}")
            
            # Kiểm tra thông số tọa độ vùng chọn
            match_sX = curr_startX == s_X
            print(f"-> startX:        [Trước] {curr_startX} {'==' if match_sX else '!='} [Sau] {s_X}")
            
            match_sY = curr_startY == s_Y
            print(f"-> startY:        [Trước] {curr_startY} {'==' if match_sY else '!='} [Sau] {s_Y}")
            
            match_eX = curr_endX == e_X
            print(f"-> endX:          [Trước] {curr_endX} {'==' if match_eX else '!='} [Sau] {e_X}")
            
            match_eY = curr_endY == e_Y
            print(f"-> endY:          [Trước] {curr_endY} {'==' if match_eY else '!='} [Sau] {e_Y}")
            
            # 5. Tổng kết kết quả
            is_match = (match_id and match_capture and match_reality and 
                        match_sX and match_sY and match_eX and match_eY)
            
            print("-"*60)
            print(f"==> KẾT QUẢ SO SÁNH: {'TRÙNG KHỚP (True)' if is_match else 'KHÔNG TRÙNG KHỚP (False)'}")
            print("="*60 + "\n")
            
            return is_match