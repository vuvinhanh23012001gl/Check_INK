from app.container import ServiceContainer,EnumMode
import json
from datetime import datetime, timezone
from app.config.path_config import PATH_FOLDER_OUTPUT

class StageExport:
    def __init__(self,service:ServiceContainer):
        self.service =  service

    def run(self):
        """Tổng hợp kết quả sản phẩm, lưu file và chờ chu kỳ Reset tiếp theo.

        Input: kết quả point từ ``service.runtime_state``.
        Output: đường dẫn file JSON tổng hợp.
        Errors: ``RuntimeError`` nếu không có kết quả để export.
        """
        results = self.service.runtime_state.get_product_result()
        if not isinstance(results, list) or not results:
            raise RuntimeError("Không có kết quả sản phẩm để export")
        PATH_FOLDER_OUTPUT.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_path = PATH_FOLDER_OUTPUT / f"judgment_result_{timestamp}.json"
        payload = {
            "product_id": results[0].get("product_id"),
            "overall": all(result.get("overall") is True for result in results),
            "status": "OK" if all(result.get("overall") is True for result in results) else "NG",
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "points": results,
        }
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.service.send_judgment_log(f"✅ Đã lưu kết quả: {output_path.name}")
        self.service.set_mode(EnumMode.MODE_IDLE)
        return str(output_path)
        
