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

## 3. Quy chuẩn Hiển thị Tiến trình Runtime khi AI làm việc (Runtime Transparency & Step-by-Step Narration)

Khi Agent thực hiện bất kỳ yêu cầu nào (đọc code, phân tích, chạy lệnh, sửa code, debug), **bắt buộc phải tường thuật rõ ràng từng bước theo thời gian thực (Step-by-Step Runtime Narration)** bằng tiếng Việt để người dùng luôn nắm bắt được AI đang làm gì. Tuyệt đối không âm thầm gọi hàng loạt tool mà không giải thích cho người dùng.

### Quy trình 5 bước hiển thị Runtime bắt buộc:

1. **Bước 1: Nêu ý định và kế hoạch ban đầu (Initial Plan & Intent)**
   - Ngay khi nhận yêu cầu, trước khi gọi bất kỳ tool nào, thông báo ngắn gọn cho người dùng:
     - Mục tiêu cần giải quyết là gì.
     - Dự kiến sẽ tra cứu ở đâu, kiểm tra file/module nào trước.
   - *Ví dụ mẫu*:
     > *"Tôi sẽ rà lại quy tắc `.agents` hiện tại và lần theo log thực tế từ tín hiệu bắt đầu runtime đến giao diện; đồng thời kiểm tra cấu trúc graphify có cách truy vấn khả dụng không. Sau đó tôi sẽ chỉnh riêng cách trình bày log và xác nhận chính xác những log nào được gửi."*

2. **Bước 2: Báo cáo công cụ, lệnh thực thi và trạng thái môi trường (Execution Transparency)**
   - Khi chạy lệnh terminal hoặc công cụ kiểm tra (Graphify, Git, Search, v.v.):
     - Nói rõ lệnh/công cụ sắp dùng và lý do sử dụng.
     - Nếu phát sinh vấn đề môi trường (ví dụ: CLI vắng mặt, dùng venv thay thế), giải thích rõ cách khắc phục trước khi chạy.
   - *Ví dụ mẫu*:
     > *"` .agents` hiện yêu cầu Graphify trước khi khoanh vùng và cập nhật sau sửa; CLI `graphify` đã vắng mặt nhưng tool search cũng không có công cụ truy vấn graph. Tôi thử đường chạy module trong venv theo cách repo ghi, rồi nếu không khả dụng sẽ giới hạn đọc đúng các node/file liên quan thay vì quét rộng."*

3. **Bước 3: Tóm tắt phát hiện ngay sau mỗi bước tra cứu (Intermediate Findings & Reasoning)**
   - Sau khi đọc code hoặc chạy lệnh Graphify, không im lặng làm tiếp mà phải tóm tắt ngay các phát hiện kỹ thuật quan trọng:
     - Node nào gọi node nào, quan hệ trực tiếp ra sao.
     - Đoạn code, hàm hoặc CSS nào đang gây ra lỗi (Root Cause).
   - *Ví dụ mẫu*:
     > *"Graphify đã xác nhận quan hệ trực tiếp: `_process_point()` được gọi bởi Stage 2 và là nơi phát log per-point; truy vấn explain đã thu gọn còn 11 cạnh. Tôi đang truy vấn riêng nhánh reset/start và tìm CSS của ô log để sửa bố cục mà không đụng các phần UI khác."*
     > *"Đã thấy nguyên nhân: `.paner-main-show-log` đang là `display: flex` mặc định theo hàng, nên mỗi `<p>` thành một cột; do đó chiều cao trông như không cuộn và log bị bó hẹp. Tôi đang kiểm tra giới hạn chiều cao của panel để sửa..."*

4. **Bước 4: Giải thích rõ ràng trước và trong khi sửa code (Pre-edit Explanation)**
   - Trước khi gọi `replace_file_content` hoặc `multi_replace_file_content`:
     - Nêu rõ tên file sẽ sửa, vị trí dòng, hàm nào bị can thiệp.
     - Giải thích lý do tại sao sửa như vậy và tác động dự kiến để tránh làm hỏng các phần khác.
   - *Ví dụ mẫu*:
     > *"Tôi tiến hành sửa file `home.js` tại hàm render log: đổi hướng flex sang `flex-direction: column` và bổ sung `overflow-y: auto`, `\n` cho từng dòng log để người dùng cuộn xem dễ dàng mà không phá vỡ layout tổng thể."*

5. **Bước 5: Xác nhận sau khi sửa & Đồng bộ hóa (Verification & Sync)**
   - Báo cáo kết quả sau khi chỉnh sửa thành công.
   - Chạy lệnh cập nhật đồ thị tri thức `graphify update .` (hoặc lệnh test).
   - Tổng kết rõ ràng cho người dùng những gì đã thay đổi và hướng xử lý tiếp theo.

---

## 4. Tiêu chuẩn phán định OK/NG của các line trong đo độ rộng đường hàn

runtime  = 0 NG level1
0< distance runtime<= level 1 thì NG levl 1
level1 < distance runtime <= level2 thì NG level2
level 2 < distance runtime <=level3 thì NG level 3
level3 <  distance runtime <=level 4 thì OK
level4 <  distance runtime <=level 5 thì OK
distance runtimec >level 5 thì NG.

