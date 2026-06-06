from app.core import Result, ErrorCode
from app.model import Calibration  
from app.services import PointService
from app.repository import CalibrationReponsitory 

import statistics

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
        Chức năng: Lấy thông số cấu hình Calibration của một Frame cụ thể.
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        
        # 1. Kiểm tra sự tồn tại của cặp ID từ hệ thống gốc của PointService
        id_tree = self.point_service.get_product_frame_id_tree()
        if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
            
        # 2. Tìm dữ liệu cấu hình trong RAM
        calib = self.calibrations.get(p_id_str, {}).get(f_id_str)
        if not calib:
            # Khởi tạo thực thể mặc định phòng ngừa crash
            calib = Calibration()
            
        return Result.Ok(calib)

    def add_calibration(self, product_id: int, frame_id: int, calib_data: dict) -> Result:
        """
        Chức năng: Tạo mới hoàn toàn cấu hình Calibration cho một Frame (Không ghi đè nếu đã có).
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        
        # 1. Xác thực cấu trúc ID hệ thống hợp lệ
        id_tree = self.point_service.get_product_frame_id_tree()
        if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)
            
        # 2. Ngăn chặn việc ghi đè cấu hình trùng lặp
        if p_id_str in self.calibrations and f_id_str in self.calibrations[p_id_str]:
            return Result.Fail(ErrorCode.CALIBRATION_ALREADY_EXISTS)

        # 3. Cập nhật dữ liệu vào RAM và lưu trữ trực tiếp
        if p_id_str not in self.calibrations:
            self.calibrations[p_id_str] = {}
        self.calibrations[p_id_str][f_id_str] = Calibration.from_dict(calib_data)
        self._sync_to_repository()
            
        return Result.Ok(self.calibrations[p_id_str][f_id_str])


    def update_calibration(self, product_id: int, frame_id: int, calib_data: dict) -> Result:
        """
        Chức năng: Cập nhật sửa đổi/thiết lập lại thông số Calibration cho một Frame đã có.
        """
        p_id_str, f_id_str = str(product_id), str(frame_id)
        
        # 1. Xác thực ID hệ thống
        id_tree = self.point_service.get_product_frame_id_tree()
        if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)

        # 2. Cập nhật RAM dữ liệu mới và đồng bộ xuống Repo
        if p_id_str not in self.calibrations:
            self.calibrations[p_id_str] = {}
        self.calibrations[p_id_str][f_id_str] = Calibration.from_dict(calib_data)
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
    

    def calculate_scale_for_frame_id(self,ID,frameID,pixel_list, reality_length,z_thresh=3.5 ):
    
        """
        Calibration pixel → mm scale cho từng frame:
        Input:
            - pixel_list: list pixel đo được
            - reality_length: mm thực tế
        Output:
            - cập nhật Calibration object trong RAM + repository
        """
        p_id_str = str(ID)
        f_id_str = str(frameID)

        id_tree = self.point_service.get_product_frame_id_tree()
        if p_id_str not in id_tree or f_id_str not in id_tree[p_id_str]:
            return Result.Fail(ErrorCode.FRAME_NOT_FOUND)


        if not pixel_list:
            return Result.Fail(ErrorCode.CALIBRATION_EMPTY_DATA)

        if len(pixel_list) < 5:
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
                z_score = 0.6745 * (x - median_pixel) / mad
                if abs(z_score) <= z_thresh:
                    filtered.append(x)

        if len(filtered) < 3:
            return Result.Fail(ErrorCode.CALIBRATION_FILTERED_TOO_MUCH)
        pixel_mean = statistics.mean(filtered)
        pixel_std = statistics.stdev(filtered)

        if pixel_mean == 0:
            return Result.Fail(ErrorCode.CALIBRATION_INVALID_MEAN)

        scale = reality_length / pixel_mean
        scale_error = scale * (pixel_std / pixel_mean)

        cv = pixel_std / pixel_mean

        confidence = max(0.0, min(1.0, 1.0 - cv))
        confidence *= min(1.0, len(filtered) / 10)

        calib = Calibration(
            reality_mm=reality_length,
            pixel_mean=pixel_mean,
            pixel_std=pixel_std,
            cv=cv,
            scale_mm_per_pixel=scale,
            scale_error_mm_per_pixel=scale_error,
            confidence=confidence,
            samples_used=len(filtered),
            samples_raw=len(pixel_list),
            mad=mad
        )
        if p_id_str not in self.calibrations:
            self.calibrations[p_id_str] = {}

        self.calibrations[p_id_str][f_id_str] = calib
        self._sync_to_repository()
        return Result.Ok(calib)