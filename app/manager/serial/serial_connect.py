import serial
import serial.tools.list_ports
from app.model import SerialConfig
from app.repository import ComRepository


class SerialConnect:
    def __init__( self,repository:ComRepository):

        self.ser = None
        self.repository = repository
        self.config = self.load_config()

    def load_config(
        self
    ) -> SerialConfig:
        data = self.repository.load_config()
        if not data:
            print(
                "File config COM rỗng"
            )
            return SerialConfig()

        return SerialConfig.from_dict(
            data
        )

    def save_config(
        self
    ):
        self.repository.save_config(
            self.config.to_dict()
        )



    def update_config(
        self,
        config: SerialConfig
    ):
        self.config = config
        self.save_config()


    def open_port(
        self
    ) -> bool:
        """Mở cổng COM và chỉ thành công khi handle thực sự đang mở.

        Input: không có; sử dụng cấu hình COM hiện tại.
        Output: ``True`` nếu pyserial tạo được handle đang mở, ngược lại ``False``.
        Errors: lỗi pyserial hoặc lỗi hệ điều hành được ghi log và không lan ra ngoài.
        """

        if not self.config.is_valid():
            print({
                "type": "software",
                "level": "warning",
                "data": "Chưa cấu hình cổng COM"
            })
            return False
        if self.ser and self.ser.is_open:

            print(
                f"COM {self.config.device_port} đã mở"
            )

            return True
        try:

            opened_serial = serial.Serial(
                port=self.config.device_port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.timeout
            )
            if not opened_serial.is_open:
                opened_serial.close()
                self.ser = None
                print(f"Mở COM {self.config.device_port} thất bại: handle đã đóng")
                return False
            self.ser = opened_serial
            print(
                f"Mở COM {self.config.device_port} thành công"
            )

            print({
                "type": "software",
                "level": "info",
                "data": (
                    f"Mở COM "
                    f"{self.config.device_port} "
                    f"thành công"
                )
            })

            return True

        except (serial.SerialException, OSError) as e:

            self.ser = None

            print(e)

            print({
                "type": "software",
                "level": "error",
                "data": (
                    f"Không thể mở "
                    f"{self.config.device_port}"
                )
            })

            return False


    def open_manual(
        self,
        port,
        baudrate
    ) -> bool:

        config = SerialConfig(
            device_port=port,
            baudrate=baudrate
        )

        self.update_config(
            config
        )

        return self.open_port()
    

    def close_port(
        self
    ):
        """Đóng handle COM hiện tại và xóa trạng thái kết nối.

        Input: không có.
        Output: không trả về giá trị.
        Errors: lỗi khi đóng được ghi log; trạng thái handle vẫn được xóa.
        """
        if not self.ser:
            return
        port_name = self.config.device_port
        try:
            self.ser.close()
        except Exception as e:
            print(e)
        finally:
            self.ser = None
            print(f"Đóng COM {port_name}")
            print({
                "type": "software",
                "level": "info",
                "data": f"Đóng COM {port_name}"
            })

    def send_data(
        self,
        data
    ) -> bool:
        """Ghi một lệnh xuống COM đang mở.

        Input: ``data`` là chuỗi lệnh không kèm newline cuối.
        Output: ``True`` nếu ghi thành công, ngược lại ``False``.
        Errors: lỗi Serial được ghi log, đóng handle hỏng và trả về ``False``.
        """
        if not self.ser or not self.ser.is_open:
            print(
                "COM chưa mở"
            )
            return False

        try:
            data_send = (
                f"{data}\n"
                .encode("utf-8")
            )
            self.ser.write(
                data_send
            )
            print(
                f"PC Send: {data}"
            )
            return True
        except Exception as e:

            print(e)
            self.close_port()
            return False


    def receive_data(
        self
    ):
        if not self.ser or not self.ser.is_open:

            return None
        try:
            if self.ser.in_waiting > 0:
                data = (
                    self.ser.readline()
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                    .strip()
                )
                print(
                    f"MCU Send:{data}"
                )
                return data
        except Exception as e:
            print(e)
            self.close_port()
        return None


    @staticmethod
    def check_port_exists(
        port_name
    ) -> bool:

        ports = (
            serial.tools
            .list_ports
            .comports()
        )

        for port in ports:

            if port.device == port_name:

                return True

        return False

    @staticmethod
    def is_port_busy(
        port_name
    ) -> bool:
    
        """
        Kiểm tra cổng serial có đang bị sử dụng hay không.

        Args:
            port_name (str): Tên cổng serial (ví dụ: COM3, COM5).

        Returns:
            bool:
                True  -> Cổng đang bị sử dụng hoặc không mở được.
                False -> Cổng đang rảnh và có thể sử dụng.
        """

        try:

            test_ser = serial.Serial(
                port_name
            )

            test_ser.close()

            return False

        except serial.SerialException:

            return True

 
    @staticmethod
    def list_ports():
        arr_ports = []
        ports = (
            serial.tools
            .list_ports
            .comports()
        )
        for port in ports:
            arr_ports.append({
                "device": port.device,
                "description": port.description
            })
        return arr_ports

    @staticmethod
    def show_port_info():
        ports = (
            serial.tools
            .list_ports
            .comports()
        )
        if not ports:
            print(
                "Không có COM nào"
            )
            return
        for port in ports:
            print(
                f"COM: {port.device}"
            )
            print(
                f"Description: {port.description}"
            )
            print(
                f"HWID: {port.hwid}"
            )
            print(
                "-" * 30
            )