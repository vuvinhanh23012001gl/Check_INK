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

            self.ser = serial.Serial(
                port=self.config.device_port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.timeout
            )
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

        except Exception as e:

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
        if not self.ser:
            return
        try:

            port_name = (
                self.config.device_port
            )

            self.ser.close()

            self.ser = None

            print(
                f"Đóng COM {port_name}"
            )

            print({
                "type": "software",
                "level": "info",
                "data": (
                    f"Đóng COM "
                    f"{port_name}"
                )
            })
        except Exception as e:
            print(e)

    def send_data(
        self,
        data
    ):
        if not self.ser:
            print(
                "COM chưa mở"
            )
            return

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
        except Exception as e:

            print(e)


    def receive_data(
        self
    ):
        if not self.ser:

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