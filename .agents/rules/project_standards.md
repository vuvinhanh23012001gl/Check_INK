---
trigger: always_on
---

# Quy chuẩn Dự án Python Detect Width Line

## 1. Nguyên tắc kiến trúc cốt lõi
- **Không phá vỡ Pipeline 3 giai đoạn**: Mọi xử lý chính phải tuân thủ tuần tự qua `StagePreprocess` -> `StageTransform` -> `StageExport` trong `app/pipeline.py`.
- **Tập trung hóa khởi tạo**: Tất cả dịch vụ phần cứng, mô hình AI và repository phải được quản lý và khởi tạo qua `ServiceContainer` (`app/container.py`). Không khởi tạo tự do trong router.
- **Luồng dữ liệu Realtime**: Không can thiệp trực tiếp vào UI socket; mọi log trả về màn hình phải đẩy qua `queue_log_send_client` với định dạng `{"type": "log_Home", "message": "..."}`.

---

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
- **Quy định**: 100% các hàm mới hoặc khi chỉnh sửa hàm cũ phải có đầy đủ Type Hint cho tham số đầu vào và kiểu trả về (`Optional`, `Union`, `List`, `Dict`, `Tuple`, `Any`, `np.ndarray`).
- **Ví dụ**:
  ```python
  def detect_anomaly(image: np.ndarray, threshold: float = 0.5) -> Tuple[bool, List[Dict[str, Any]]]:
      ...
  ```

### 2.3. Xử lý ngoại lệ (Exception Handling) & Bảo vệ luồng
- Tuyệt đối **không** dùng `except: pass` bỏ qua lỗi âm thầm.
- Các hàm trong worker chạy ngầm (`threading.Thread`) hoặc bên trong 3 Stage của `Pipeline` bắt buộc phải có khối `try...except Exception as e:` bao bọc, ghi log chi tiết và đẩy thông báo lỗi vào hàng đợi log:
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
- Giữ nguyên logic bắt cạnh sườn (rising edge: `current_state and not previous_state`) ở các hàm đọc nút bấm vật lý (nút Reset, Start, Sensor an toàn).
- Không tự ý xóa hoặc giảm thời gian `time.sleep(0.05)` trong các vòng lặp theo dõi IO/Serial để tránh chiếm dụng 100% CPU.
- Không thay đổi cấu trúc bản tin Serial (baudrate, byte cờ báo, ACK/NACK handshake) giữa máy tính với vi điều khiển STM32/IAI nếu không có chỉ định trực tiếp từ người dùng.

---

## 3. Quy chuẩn Hiển thị Tiến trình Runtime (Runtime Transparency)
Khi Agent thực hiện tác vụ (tra cứu, đọc code, chạy lệnh, sửa code), phải tường thuật **ngắn gọn 1-2 câu súc tích** để người dùng theo dõi mà không làm loãng context:

1. **Trước khi tra cứu / gọi tool**: Nêu ngắn gọn mục tiêu và công cụ/file sắp truy vấn.
2. **Sau khi có kết quả tra cứu**: Tóm tắt ngay phát hiện kỹ thuật trọng yếu (quan hệ hàm, nguyên nhân gốc rễ).
3. **Trước khi sửa code**: Chỉ rõ tên file, vị trí dòng, hàm sẽ sửa và lý do kỹ thuật.
4. **Sau khi hoàn tất sửa**: Xác nhận kết quả và chạy `graphify update .` để đồng bộ đồ thị tri thức.

---

## 4. Tiêu chuẩn phán định OK/NG đo độ rộng đường hàn (`StageTransform`)
Quy tắc phán định giá trị khoảng cách đường hàn thực tế (`distance_runtime`) so với các ngưỡng cài đặt (`level1` đến `level5` theo thứ tự tăng dần):

- `distance_runtime == 0`: **NG level 1** *(Không phát hiện đường hàn hoặc mất điểm đo)*
- `0 < distance_runtime <= level1`: **NG level 1** *(Đường hàn quá mảnh/mất nét nghiêm trọng)*
- `level1 < distance_runtime <= level2`: **NG level 2** *(Đường hàn nhỏ dưới ngưỡng tiêu chuẩn)*
- `level2 < distance_runtime <= level3`: **NG level 3** *(Đường hàn hơi mảnh sát biên)*
- `level3 < distance_runtime <= level5`: **OK** *(Đường hàn đạt tiêu chuẩn chất lượng)*
- `distance_runtime > level5`: **NG** *(Đường hàn quá to/loang vượt ngưỡng tối đa)*
