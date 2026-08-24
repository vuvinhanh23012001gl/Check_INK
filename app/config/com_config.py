from dataclasses import asdict, dataclass
from typing import Any

from app.model.serial import SerialConfig


@dataclass
class ComConfig:
    """Cấu hình kết nối COM ở biên config của ứng dụng.

    Input: tên cổng COM và baudrate từ giao diện web hoặc ``SerialConfig``.
    Output: object cấu hình COM và dictionary JSON-compatible.
    Errors: ``ValueError`` nếu cổng rỗng hoặc baudrate không hợp lệ.
    """

    port_name: str | None = None
    baudrate: int = 115200


    @classmethod
    def from_serial_config(cls, config: SerialConfig) -> "ComConfig":
        """Tạo cấu hình web từ cấu hình serial đang được sử dụng.

        Input: instance ``SerialConfig``.
        Output: instance ``ComConfig``.
        Errors: không phát sinh với instance hợp lệ.
        """
        return cls(config.device_port, int(config.baudrate))

    @classmethod
    def from_values(cls, port_name: str, baudrate: Any) -> "ComConfig":
        """Chuẩn hóa và xác thực giá trị nhận từ API.

        Input: tên cổng và baudrate bất kỳ từ request.
        Output: ``ComConfig`` đã chuẩn hóa.
        Errors: ``ValueError`` nếu giá trị không hợp lệ.
        """
        if not isinstance(port_name, str) or not port_name.strip():
            raise ValueError("port_name is required")
        try:
            normalized_baudrate = int(baudrate)
        except (TypeError, ValueError) as error:
            raise ValueError("baudrate must be an integer") from error
        if normalized_baudrate <= 0:
            raise ValueError("baudrate must be greater than 0")
        return cls(port_name.strip(), normalized_baudrate)

    def to_serial_config(self) -> SerialConfig:
        """Chuyển sang cấu hình mà lớp serial hiện tại sử dụng.

        Input: cấu hình COM đã hợp lệ.
        Output: instance ``SerialConfig``.
        Errors: ``ValueError`` nếu cấu hình chưa hợp lệ.
        """
        self.validate()
        return SerialConfig(device_port=self.port_name, baudrate=self.baudrate)

    def validate(self) -> None:
        """Kiểm tra cấu hình trước khi lưu hoặc mở cổng.

        Input: không có.
        Output: không trả về nếu hợp lệ.
        Errors: ``ValueError`` nếu thiếu cổng hoặc baudrate không dương.
        """
        if not isinstance(self.port_name, str) or not self.port_name.strip():
            raise ValueError("port_name is required")
        if int(self.baudrate) <= 0:
            raise ValueError("baudrate must be greater than 0")

    def to_dict(self) -> dict[str, Any]:
        """Trả về dữ liệu cấu hình dùng cho API và log.

        Input: không có.
        Output: dictionary gồm ``port_name`` và ``baudrate``.
        Errors: không phát sinh.
        """
        return asdict(self)