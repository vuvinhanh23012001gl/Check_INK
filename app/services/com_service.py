from app.manager.serial import ManagerSerial
from app.model import SerialConfig
from app.config import ComConfig
import time
import threading

FORMAT_COMAND_SEND_ARM  =  "cmd:"
TIME_OUT_WAIT_ARM_RESEND = 4

class ComService:
   
    def __init__(self, manager_serial:ManagerSerial):
        self.manager = manager_serial

        self._lock = threading.Lock()
        self.shake_hands_compelete = False # Cai nay se duoc pipeline luồng khác tự động bật lên khi hand sharak thành công.
        
    def set_shake_hands_complete(self, value: bool):
        with self._lock:
            self.shake_hands_compelete = value

    def get_shake_hands_complete(self) -> bool:
        with self._lock:
            return self.shake_hands_compelete

    def get_configuration_data(self):
        """Lấy cấu hình COM hiện tại và danh sách cổng serial trên máy.

        Input: không có.
        Output: dictionary gồm cấu hình, danh sách cổng và trạng thái kết nối.
        Errors: lỗi liệt kê cổng được trả về dưới dạng danh sách rỗng.
        """
        try:
            ports = self.manager.serial_com.list_ports()
        except Exception as error:
            print(f"[ComService] List ports failed: {error}")
            ports = []
        config = ComConfig.from_serial_config(self.manager.serial_com.config)
        return {
            "config": config.to_dict(),
            "ports": ports,
            "connected": bool(self.manager.serial_com.ser and self.manager.serial_com.ser.is_open),
        }


    def configure_connection(self, port_name: str, baudrate: int) -> dict:
        """Đổi cổng COM, lưu cấu hình và yêu cầu ManagerSerial kết nối lại.

        Input: ``port_name`` là tên cổng COM; ``baudrate`` là tốc độ truyền.
        Output: dictionary gồm trạng thái mở cổng, cấu hình hiện tại,
            trạng thái kết nối và danh sách cổng COM đang có.
        Errors: ``ValueError`` nếu payload sai; kết nối thất bại được trả về
            trong ``success=False`` để giao diện vẫn có thể hiển thị kết quả.
        """
        requested_config = ComConfig.from_values(port_name, baudrate)
        previous_config = self.manager.serial_com.config.to_dict()
        status = self.manager.update_com(
            requested_config.port_name,
            requested_config.baudrate,
        )
        if not status:
            self.manager.serial_com.config = SerialConfig.from_dict(previous_config)
            self.manager.serial_com.save_config()
            print("[ComService] Kết nối thất bại, đã khôi phục COM.json trước đó")
        result = self.get_configuration_data()
        result["success"] = status
        result["message"] = (
            "Mở và lưu cổng COM thành công"
            if status
            else "Không thể mở cổng COM đã chọn"
        )
        return result

    def send_and_wait(self, x, y, z, timeout = TIME_OUT_WAIT_ARM_RESEND):
        """
        Gửi dữ liệu và chờ ARM xác nhận.
        Returns:
            True  : nhận đúng phản hồi
            False : timeout hoặc phản hồi sai
        """
        try:
            # Tạo chuỗi dữ liệu giống hàm send()
            data_send = f"{FORMAT_COMAND_SEND_ARM}{int(x)},{int(y)},{int(z)},80"
            self.manager.send_data(data_send)
            # Chờ phản hồi
            return self.wait_for_specific_data(
                expected_message=data_send,
                timeout=timeout
            )
        except Exception as e:
            print(f"❌ Lỗi send_and_wait: {e}")
        return False
    

    def check_format_data(self, string_data ):
        """Kiểm tra dữ liệu có đúng định dạng không và chuyển đổi về định dạng chuẩn.
            Ví dụ: 'cmd:1,2,3' -> 'cmd:001,002,003,ok'"""
        if not string_data:
            print("❌ Dữ liệu bị lỗi hoặc trống, không có dữ liệu để so sánh.")
            return False
        if string_data.startswith(f"{FORMAT_COMAND_SEND_ARM}"):
            raw_data = string_data[4:].split(",")
            raw_data = [x.strip() for x in raw_data if x.strip() != ""]
            if not raw_data:
                print("❌ Không có dữ liệu tọa độ sau 'cmd:'")
                return False
            arr_covert_text = ["cmd:"]
            for i in raw_data:
                try:
                    padded = f"{int(i):03}"
                except ValueError:
                    print(f"⚠️ Không thể chuyển '{i}' thành số nguyên.")
                    return False
                arr_covert_text.append(padded)
            arr_covert_text.append("ok")
            s = ",".join(arr_covert_text[1:])
            s = f"{FORMAT_COMAND_SEND_ARM}"+s
            return s
        else:
            print("❌ Không phải dữ liệu tọa độ (không bắt đầu bằng 'cmd:')")
            return False
        


    def wait_for_specific_data(self, expected_message, timeout = TIME_OUT_WAIT_ARM_RESEND):
        """Hàm này chờ tín hiệu cụ thể từ manager_serial.Chờ thời gian timeout giây.Sau thời gian chờ k được gửi về False.Nếu nhận đúng tín hiệu trả về True"""
        print(f"⏳ Đang chờ tín hiệu:{expected_message} trong {timeout} giây...")
        start_time = time.time()
        expected = self.check_format_data(expected_message) 
        while time.time() - start_time < timeout:
            data = self.manager.get_data_from_queue()
            if data:
                print(f"📥 PC Nhận được: {data}")
                print("📥 Sau chuyển đổi :", expected)
                if data.strip() == expected:
                    now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(now_str,"✅ Nhận đúng tín hiệu mong đợi.")
                    return True
                else:
                    print("⚠️ Tín hiệu nhận sai nội dung.")
            time.sleep(0.001)
        print(f"❌ Timeout: Không nhận được tín hiệu trong {timeout} giây.")
        return False
    
    
                


