# Module: Hardware Integration (IAI RoboCylinder & Industrial Camera)

## 1. Tổng quan
Hệ thống kiểm tra ngoại quan và khe hàn tương tác trực tiếp với 2 nhóm phần cứng công nghiệp chủ chốt:
1. **Bộ truyền động tuyến tính IAI RoboCylinder & IO Controller**: Di chuyển camera đến các vị trí đo (Frame/Point), đọc tín hiệu an toàn (Safety sensor, limit sensor), nhận lệnh Start/Stop/Reset từ nút ấn vật lý, và điều khiển tháp đèn (Red, Blue, Yellow, Buzzer).
2. **Camera công nghiệp Omron Sentech (GenICam / StApi)**: Chụp ảnh độ phân giải cao tại các tọa độ dừng, đồng bộ hóa trigger qua phần mềm hoặc tín hiệu phần cứng.

---

## 2. IAI Motion & IO Control (`app/machine/iaicontrol.py`, `app/manager/serial/`)

### 2.1. Cấu trúc quản lý cổng nối tiếp (Serial Manager)
Lớp [`ManagerSerial`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/manager/serial/serial_manager.py) triển khai mô hình Producer-Consumer đa luồng, cách ly hoàn toàn việc đọc/ghi UART/RS232 khỏi luồng chính:
- **`SerialConnect`**: Đóng gói thư viện `pyserial`, thiết lập baudrate, parity, timeout, và tự động kiểm tra `is_open`.
- **`rx_thread`**: Luôn lắng nghe dữ liệu từ cổng COM và đẩy vào các `Queue` đăng ký (`subscribe_rx()`).
- **`tx_thread`**: Lấy lệnh từ hàng đợi `tx_queue` và gửi tuần tự xuống thiết bị, tránh xung đột ghi đồng thời giữa các thread.
- **`check_thread` (`CheckCOM`)**: Luồng daemon định kỳ thăm dò trạng thái kết nối phần cứng; phát hiện ngắt cáp USB/COM để kích hoạt quy trình tái kết nối (Reconnect loop).

```
   [Application Threads]
       │             ▲
       ▼ (tx_queue)  │ (rx_queue / subscribers)
   ┌───────────────────────┐
   │     ManagerSerial     │
   ├───────────┬───────────┤
   │ tx_thread │ rx_thread │
   └─────┬─────┴─────▲─────┘
         │           │
         ▼           │
     [Serial Port / RS232]
               │
               ▼
     [IAI Controller & IO]
```

### 2.2. Điều khiển chuyển động và trạng thái thiết bị (`IAIControl`)
Class [`IAIControl`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/machine/iaicontrol.py) quản lý chu trình vận hành của robot:
- **Origin Return (Về gốc / Homing)**: Đưa trục về vị trí tọa độ 0 chuẩn để đồng bộ hóa tọa độ cơ khí.
- **Position Moving (`move_to_position`)**: Di chuyển trục đến vị trí mm cụ thể với gia tốc và vận tốc cấu hình.
- **Safety Interlock**:
  - `sensor_safety`: Cảm biến rào quang an toàn. Khi bị che (xâm phạm vùng nguy hiểm), tự động kích hoạt `pause_because_sensor_safety`.
  - `sensor_left_distance` & `sensor_right_distance`: Giới hạn hành trình cơ khí.
- **Signal Tower & Annunciation**:
  - `led_out_red`, `led_out_blue`, `led_out_yellow`, `buzzer_out`.
  - Quản lý nhấp nháy đèn theo chu kỳ thời gian thực (`last_blink_time`) cho các trạng thái: Chờ (Standby), Đang chạy (Running), Lỗi/Cảnh báo (Alarm/NG).

---

## 3. Industrial Camera Integration (`app/services/camera/camera_connect.py`)

### 3.1. Kiến trúc giao tiếp StApi (Omron Sentech)
Sử dụng SDK `stapipy` chuẩn GenICam cho camera công nghiệp:
- **Khởi tạo và cấu hình NodeMap**:
  - Mở `CStDevice` và `CStDataStream`.
  - Cấu hình thông số: `ExposureTime`, `Gain`, `PixelFormat`, `Width`, `Height`, `TriggerMode`, `TriggerSource`.
- **Luồng thu nhận ảnh liên tục (`thread_camera`)**:
  - Thu nhận buffer ảnh từ datastream thông qua cơ chế Zero-copy / Direct-memory view khi trích xuất NumPy array:
  ```python
  raw_image = st_stream_buffer.get_image()
  np_array = raw_image.get_data() # Tạo NumPy view
  ```
  - Chuyển đổi định dạng màu sắc (Mono8 / BayerRG8 / BGR8) bằng OpenCV `cv2.cvtColor`.
- **Cơ chế chụp đơn ảnh Trigger (`capture_one_image`)**:
  - Sử dụng `threading.Event()` (`self._capture_event`) và `threading.Lock()` (`self._lock_capture`) để đồng bộ:
  - Khi Pipeline yêu cầu chụp: Kích hoạt cờ `_capture_one = True` và đợi `_capture_event.wait(timeout)`.
  - Luồng thu nhận frame sẽ gán frame hiện tại vào `_captured_image` và gọi `_capture_event.set()`.

---

## 4. Cơ chế phục hồi sự cố phần cứng (Fault Tolerance & Reconnection)

| Sự cố | Cơ chế phát hiện | Hành vi xử lý của hệ thống |
| :--- | :--- | :--- |
| **Mất kết nối COM (USB bị rút)** | `ManagerSerial._check_connect` bắt lỗi `SerialException` | Đóng luồng RX/TX, chuyển cờ `com_is_open = False`, liên tục thử mở lại COM theo interval an toàn (2s). |
| **Nút Stop khẩn cấp / Rào quang** | `IAIControl.button_thread` đọc bit IO `sensor_safety` | Gửi lệnh Stop tức thì tới IAI; bật cờ `pause = True`; bật còi Buzzer và nhấp nháy đèn Đỏ. |
| **Mất kết nối Camera (Rút cáp GigE/USB)** | StApi ném `StApiError` hoặc không nhận được frame quá `TIMEOUT_WAIT_NEW_FRAME` (10s) | Gán `camera_lost = True`; giải phóng device handle; chạy luồng tái kết nối `reconnect_camera()`. |
| **Timeout nhận phản hồi IAI** | Timeout queue trong `send_command_and_wait_response` | Ném mã lỗi `ErrorCode.HARDWARE_TIMEOUT`, ghi log Socket.IO để UI hiển thị thông báo khẩn. |
