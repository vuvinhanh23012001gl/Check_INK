import json
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path

from app.config import (
    PATH_CONFIG_CALIBRATION,
    PATH_CONFIG_POINTS,
    PATH_FILE_DATA_CONFIG_JUDMENT_LAW,
    PATH_PRODUCT_CHOOSE_PRODUCT,
)
from app.container import EnumMode, ServiceContainer
from app.core.context import RuntimePipelineState


@dataclass
class PreparedProduct:
    """Dữ liệu đã chuẩn hóa để Stage 2 xử lý tuần tự."""

    product_id: str
    frames: list[dict]
    scale_mm_per_pixel: float
    session_id: str
    number_step: int

class StagePreprocess:
    """Đọc và chuẩn hóa dữ liệu sản phẩm trước khi điều khiển IAI."""
    def __init__(self,services:ServiceContainer):

        self.services = services
        self.protocol_connection_OK = False


    def run(self):
        """Nạp points, judgment law, calibration và chuyển sang Stage 2.

        Input: dữ liệu sản phẩm hiện tại trong các file JSON của storage.
        Output: lưu ``PreparedProduct`` vào container và chuyển mode sang transform.
        Errors: ``ValueError`` nếu thiếu/sai product, frame, point hoặc judgment law.
        """
        prepared = self._load_product_data()
        print(
            "[STAGE1] Chuẩn bị product="
            f"{prepared.product_id}, frames={len(prepared.frames)}, "
            f"number_step={prepared.number_step}, session={prepared.session_id}"
        )
        self.services.prepared_product = prepared
        self.services.runtime_state.set_pipeline_state(
            RuntimePipelineState.READY
        )
        self.services.set_mode(EnumMode.MODE_TRANSFORM)
        self.services.send_judgment_log(
            f"✅ Stage 1 hoàn tất: product {prepared.product_id}, "
            f"{sum(len(frame['points']) for frame in prepared.frames)} point."
        )
        return prepared

    def _read_json(self, path: str) -> dict:
        """Đọc một file JSON object.

        Input: ``path`` là đường dẫn file JSON.
        Output: object JSON dạng dict.
        Errors: ``ValueError`` nếu file không tồn tại, sai JSON hoặc không phải object.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise ValueError(f"Không tìm thấy file dữ liệu: {file_path}")
        try:
            with file_path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Không đọc được file {file_path}: {error}") from error
        if not isinstance(data, dict):
            raise ValueError(f"Dữ liệu {file_path} phải là object JSON")
        return data

    def _load_product_data(self) -> PreparedProduct:
        """Ghép bốn nguồn JSON thành danh sách frame/point có judgment config."""
        choose_data = self._read_json(PATH_PRODUCT_CHOOSE_PRODUCT)
        product_id = str(choose_data.get("product", "")).strip()
        if not product_id:
            raise ValueError("Chưa có sản phẩm hiện tại trong choose_product_select.json")

        points_data = self._read_json(PATH_CONFIG_POINTS).get(product_id)
        law_data = self._read_json(PATH_FILE_DATA_CONFIG_JUDMENT_LAW).get(product_id)
        calibration_data = self._read_json(PATH_CONFIG_CALIBRATION).get(product_id, {})
        if not isinstance(points_data, dict) or not points_data:
            raise ValueError(f"Không có points cho product {product_id}")
        if not isinstance(law_data, dict):
            raise ValueError(f"Không có config judgment cho product {product_id}")
        print(
            f"[STAGE1] Đã đọc product={product_id}: "
            f"frames_points={len(points_data)}, judgment_frames={len(law_data)}"
        )

        frames = []
        for frame_id in sorted(points_data, key=self._sort_key):
            raw_points = points_data[frame_id]
            frame_law = law_data.get(str(frame_id), {})
            if not isinstance(raw_points, dict) or not isinstance(frame_law, dict):
                raise ValueError(f"Frame {frame_id} của product {product_id} không hợp lệ")
            points = []
            for point_id in sorted(raw_points, key=self._sort_key):
                point = raw_points[point_id]
                if not isinstance(point, dict):
                    raise ValueError(f"Point {frame_id}/{point_id} không hợp lệ")
                try:
                    coordinates = {
                        "x": int(point["x"]),
                        "y": int(point["y"]),
                        "z": int(point["z"]),
                    }
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(
                        f"Point {frame_id}/{point_id} thiếu tọa độ IAI"
                    ) from error
                judgment = frame_law.get(str(point_id))
                if not isinstance(judgment, dict) or not judgment:
                    judgment = {}
                print(
                    f"[STAGE1] frame={frame_id}, item={point_id}, "
                    f"inspectors={list(judgment.keys()) if judgment else []}"
                )
                points.append({
                    "point_id": str(point_id),
                    **coordinates,
                    "judgment": judgment,
                    "source": point,
                })
            if points:
                frames.append({"frame_id": str(frame_id), "points": points})
        if not frames:
            raise ValueError(f"Product {product_id} không có frame/point hợp lệ")

        scale = self._read_scale(calibration_data)
        number_step = sum(len(frame["points"]) for frame in frames)
        session_id = datetime.now(timezone.utc).strftime("session_%Y%m%dT%H%M%S%fZ")
        return PreparedProduct(product_id, frames, scale, session_id, number_step)

    @staticmethod
    def _sort_key(value: str) -> tuple[int, str]:
        """Sắp xếp ID số trước ID chữ."""
        text = str(value)
        return (0, f"{int(text):020d}") if text.isdigit() else (1, text)

    @staticmethod
    def _read_scale(calibration_data: dict) -> float:
        """Lấy scale calibration đầu tiên hợp lệ, mặc định 1.0."""
        for frame in calibration_data.values():
            if not isinstance(frame, dict):
                continue
            result = frame.get("result_parameters", {})
            scale = result.get("scale_mm_per_pixel") if isinstance(result, dict) else None
            try:
                if scale is not None and float(scale) > 0:
                    return float(scale)
            except (TypeError, ValueError):
                continue
        return 1.0
        

    def check_protocol_connect_com(self):
    
        """Kiểm tra COM đã sẵn sàng mà không điều khiển ARM về gốc.
        Input: không có; đọc trạng thái kết nối từ ``ManagerSerial``.
        Output: ``True`` nếu COM và các luồng RX/TX đang hoạt động, ngược lại
            ``False``.
        Errors: không phát sinh; lỗi kết nối được ``ManagerSerial`` xử lý.
        """

        status = self.services.obj_manager_serial.is_running()
        if status and not self.protocol_connection_OK:
            print("✅ COM và luồng Serial đã sẵn sàng.")
            self.protocol_connection_OK = True
            self.services.obj_com_service.set_shake_hands_complete(True)
        elif not status:
            self.protocol_connection_OK = False
        return status
    


      
            


                
                
             
             
        

            
            
       














