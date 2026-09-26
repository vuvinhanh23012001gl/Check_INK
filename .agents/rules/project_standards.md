---
trigger: always_on
---

# Quy định dự án Python Detect Width Line

## 1. Nguyên tắc kiến trúc cốt lõi
- **Không phá vỡ Pipeline 3 giai đoạn**: Mọi xử lý chính phải tuân thủ tuần tự qua `StagePreprocess` -> `StageTransform` -> `StageExport` trong `app/pipeline.py`.
- **Tập trung hóa khởi tạo**: Tất cả dịch vụ phần cứng, mô hình AI và repository phải được quản lý và khởi tạo qua `ServiceContainer` (`app/container.py`). Không khởi tạo tự do trong router.
- **Luồng dữ liệu Realtime**: Không can thiệp trực tiếp vào UI socket; mọi log trả về màn hình phải đẩy qua `queue_log_send_client` với định dạng `{"type": "log_Home", "message": "..."}`.

## 2. Tiêu chuẩn viết code (Coding Standards)

### 2.1. Ngôn ngữ & Comment
- **Quy định**: Mọi chú thích giải thích logic code mới phải viết bằng **tiếng Việt có dấu**, diễn đạt rõ ràng mục đích xử lý (giải thích *lý do tại sao* làm vậy thay vì chỉ nhắc lại cú pháp).
- **Docstring**: Giữ nguyên toàn bộ docstring cũ của hệ thống. Khi viết hàm mới, bổ sung docstring chuẩn:
  ```python
  def calculate_weld_width(contour: np.ndarray, mm_per_pixel: float) -> float:
      """
      Tính toán bề rộng mối hàn thực tế dựa trên đường bao contour và tỉ lệ calibration.

      Args:
          contour (np.ndarray): Tập hợp các điểm biên của mối hàn (N, 1, 2).
          mm_per_pixel (float): Hệ số quy đổi từ pixel sang milimet.

      Returns:
          float: Bề rộng mối hàn tính bằng mm. Trả về 0.0 nếu không tìm thấy contour hợp lệ.
      """
  ```

### 2.2. Type Hinting (Ép kiểu tham số và đầu ra)
- **Quy định**: 100% các hàm mới hoặc khi chỉnh sửa hàm cũ phải có đầy đủ Type Hint cho tham số đầu vào và kiểu trả về.
- **Thư viện chuẩn**: Sử dụng kiểu từ `typing` (`Optional`, `Union`, `List`, `Dict`, `Tuple`, `Any`) và `numpy.ndarray`.
- **Ví dụ**:
  ```python
  # ❌ KHÔNG ĐẠT (Thiếu type hint):
  def detect_anomaly(image, threshold):
      ...

  # ✅ CHUẨN (Đầy đủ type hint):
  def detect_anomaly(image: np.ndarray, threshold: float = 0.5) -> Tuple[bool, List[Dict[str, Any]]]:
      ...
  ```

### 2.3. Xử lý ngoại lệ (Exception Handling) & Bảo vệ luồng
- **Quy định**:
  - Tuyệt đối **không** dùng `except: pass` bỏ qua lỗi âm thầm.
  - Các hàm trong worker chạy ngầm (`threading.Thread`) hoặc bên trong 3 Stage của `Pipeline` bắt buộc phải có khối `try...except Exception as e:` bao bọc, ghi log chi tiết (stack trace hoặc thông báo lỗi) để tránh crash sập luồng nền.
  - Mọi thông báo lỗi cần hiển thị lên giao diện người dùng phải được đẩy vào hàng đợi log:
  ```python
  try:
      # Logic xử lý thuật toán / giao tiếp phần cứng
      ...
  except Exception as e:
      error_msg = f"[LỖI][Transform] Thất bại khi phán định ảnh: {str(e)}"
      print(error_msg)
      self.services.queue_log_send_client.put({
          "type": "log_Home",
          "message": error_msg
      })
  ```

### 2.4. Phần cứng STM32 / IAI (Quy tắc bất khả xâm phạm)
- **Quy định**:
  - Giữ nguyên logic bắt cạnh sườn (rising edge: `current_state and not previous_state`) ở các hàm đọc nút bấm vật lý (như nút Reset, Start, Sensor an toàn).
  - Không tự ý xóa hoặc giảm thời gian `time.sleep(0.05)` trong các vòng lặp theo dõi IO/Serial để tránh chiếm dụng 100% CPU.
  - Không thay đổi cấu trúc bản tin Serial (baudrate, byte cờ báo, ACK/NACK handshake) giữa máy tính với vi điều khiển STM32/IAI nếu không có chỉ định trực tiếp từ người dùng.

