---
trigger: always_on
---

# AGENTS.md — Quy chuẩn phát triển dự án Python Detect Width Line

## 1. Mục đích và phạm vi áp dụng

Tài liệu này quy định các nguyên tắc bắt buộc đối với AI Agent và lập trình viên khi đọc, phân tích, sửa đổi, mở rộng hoặc bảo trì dự án Python Detect Width Line.

Mục tiêu:

* Bảo toàn kiến trúc và luồng xử lý hiện hữu.
* Ngăn chặn việc tự suy đoán yêu cầu nghiệp vụ.
* Đảm bảo tính ổn định của Pipeline và giao tiếp phần cứng.
* Duy trì chất lượng code, khả năng bảo trì và truy xuất lỗi.
* Đảm bảo mọi thay đổi đều được kiểm tra và xác minh trước khi báo cáo.

### 1.1. Thứ tự ưu tiên

Khi thực hiện công việc, phải ưu tiên theo thứ tự:

1. Yêu cầu đã được người dùng xác nhận.
2. Quy chuẩn kiến trúc và an toàn phần cứng trong tài liệu này.
3. Hành vi và logic hiện hữu của hệ thống.
4. Các tiêu chuẩn coding và khuyến nghị kỹ thuật.

Không được tự ý thay đổi các quy định ở cấp ưu tiên cao hơn để thuận tiện cho việc triển khai.

---

## 2. Nguyên tắc làm rõ yêu cầu (Requirement Clarification)

### 2.1. Không tự suy đoán yêu cầu

Đây là nguyên tắc bắt buộc áp dụng trước mọi hoạt động sửa đổi code.

* TUYỆT ĐỐI KHÔNG tự suy đoán yêu cầu nghiệp vụ, thuật toán, giao diện hoặc hành vi hệ thống khi thông tin chưa rõ ràng.
* Không tự ý lựa chọn phương án triển khai khi có nhiều cách hiểu dẫn đến kết quả hoặc hành vi khác nhau.
* Không tự ý mở rộng phạm vi công việc, bổ sung tính năng hoặc thay đổi logic ngoài yêu cầu.
* Không coi suy luận kỹ thuật của Agent là bằng chứng cho thấy phương án đó phù hợp với mong muốn của người dùng.
* Không tự diễn giải sự im lặng của người dùng thành sự đồng ý.

**Nguyên tắc cốt lõi: Thà hỏi rõ trước khi làm còn hơn tự suy diễn và sửa sai hệ thống.**

### 2.2. Các trường hợp bắt buộc hỏi lại

Agent phải tạm dừng phần triển khai liên quan và đặt câu hỏi xác nhận khi:

* Chưa rõ mục tiêu hoặc kết quả đầu ra mong muốn.
* Yêu cầu có nhiều cách hiểu hoặc nhiều phương án triển khai khác nhau.
* Chưa rõ phạm vi file, module hoặc chức năng cần thay đổi.
* Chưa xác định điều kiện đầu vào, đầu ra hoặc quy tắc nghiệp vụ.
* Chưa rõ cách xử lý dữ liệu không hợp lệ, lỗi thuật toán hoặc lỗi phần cứng.
* Yêu cầu có khả năng ảnh hưởng đến Pipeline, ServiceContainer, UI, dữ liệu lưu trữ hoặc giao tiếp STM32/IAI.
* Yêu cầu mâu thuẫn với kiến trúc hoặc logic hiện hữu.
* Có thông tin quan trọng chưa được xác nhận và việc tự lựa chọn có thể làm thay đổi hành vi hệ thống.

### 2.3. Cách đặt câu hỏi

* Đặt câu hỏi cụ thể, ngắn gọn, tập trung vào thông tin còn thiếu.
* Nếu có nhiều phương án, trình bày các lựa chọn A/B/C và giải thích ngắn sự khác biệt.
* Khi cần thiết, đưa ra ví dụ đầu vào và đầu ra dự kiến để người dùng xác nhận.
* Tổng hợp các điểm chưa rõ thành một lượt hỏi để hạn chế hỏi đi hỏi lại.
* Không hỏi lại thông tin đã được cung cấp rõ ràng hoặc có thể xác định chắc chắn từ code hiện hữu.

### 2.4. Trong thời gian chờ xác nhận

* Không sửa code theo phương án tự suy đoán.
* Có thể tiếp tục đọc code, phân tích luồng xử lý, xác định nguyên nhân hoặc chuẩn bị phương án.
* Chỉ tiếp tục các công việc độc lập nếu không phụ thuộc vào thông tin đang chờ xác nhận.
* Không thực hiện thay đổi có thể gây ảnh hưởng đến phần đang chờ xác nhận.

### 2.5. Xác nhận trước khi triển khai

Đối với yêu cầu phức tạp hoặc có ảnh hưởng đến kiến trúc, Agent phải tóm tắt:

1. Mục tiêu cần đạt.
2. Phạm vi file/module dự kiến thay đổi.
3. Logic xử lý dự kiến.
4. Hành vi hiện hữu cần bảo toàn.
5. Những điểm đã được người dùng xác nhận.

Chỉ triển khai khi các thông tin cần thiết đã rõ ràng và thống nhất.

---

## 3. Quy chuẩn kiến trúc hệ thống (Architecture Guardrails)

### 3.1. Bảo toàn Pipeline 3 giai đoạn

Mọi xử lý chính phải tuân thủ tuần tự qua ba giai đoạn trong `app/pipeline.py`:

`StagePreprocess → StageTransform → StageExport`

Trách nhiệm tổng quát:

* `StagePreprocess`: Tiền xử lý dữ liệu đầu vào.
* `StageTransform`: Thực hiện xử lý thuật toán, phân tích và phán định.
* `StageExport`: Xuất kết quả theo cơ chế hiện hữu.

Quy định:

* Không tự ý tạo thêm Pipeline hoặc thay đổi thứ tự các Stage.
* Không chuyển logic nghiệp vụ từ Stage sang Router hoặc UI.
* Không bỏ qua Stage để xử lý trực tiếp dữ liệu ở module khác.
* Không chuyển dữ liệu chưa hợp lệ sang giai đoạn tiếp theo.
* Ưu tiên tái sử dụng các hàm xử lý hiện có trước khi tạo mới.

### 3.2. Tập trung hóa khởi tạo dịch vụ

Tất cả dịch vụ phần cứng, mô hình AI và Repository phải được quản lý thông qua `ServiceContainer` tại `app/container.py`.

* Không khởi tạo tùy tiện các dịch vụ trong Router.
* Không tạo thêm instance của dịch vụ đã được quản lý bởi ServiceContainer.
* Không tự ý thay đổi vòng đời hoặc cơ chế khởi tạo dịch vụ.
* Không tạo thêm ServiceContainer nếu chưa có yêu cầu và chưa xác định được sự cần thiết.

### 3.3. Bảo toàn giao diện và API hiện hữu

* Không tự ý đổi tên class, hàm, biến cấu hình hoặc module đang được sử dụng.
* Không thay đổi chữ ký API, cấu trúc dữ liệu đầu vào/đầu ra hoặc giao diện giữa các module nếu chưa được yêu cầu.
* Không xóa code cũ chỉ vì chưa thấy được sử dụng.
* Không tự ý refactor toàn bộ file khi chỉ cần sửa một chức năng.
* Ưu tiên thay đổi tối thiểu, đúng phạm vi yêu cầu.

---

## 4. Quy chuẩn giao tiếp Realtime và Logging

### 4.2. Quy định ghi log

* Log phải thể hiện rõ chức năng hoặc giai đoạn phát sinh lỗi.
* Thông báo lỗi phải đủ thông tin để xác định nguyên nhân và vị trí xử lý.
* Không bỏ qua lỗi một cách âm thầm.
* Không tự ý thay đổi cấu trúc bản tin đang được UI sử dụng.
* Ưu tiên sử dụng cơ chế logging hiện hữu của dự án; không tự ý tạo thêm hệ thống logging song song.

---

## 5. Tiêu chuẩn viết code (Coding Standards)

### 5.1. Ngôn ngữ và chú thích

* Mọi comment giải thích logic code mới phải viết bằng tiếng Việt có dấu.
* Comment cần giải thích mục đích hoặc lý do xử lý, không chỉ nhắc lại cú pháp.
* Giữ nguyên toàn bộ docstring cũ của hệ thống.
* Không tự ý xóa hoặc viết lại docstring cũ nếu không có yêu cầu.

### 5.2. Docstring cho hàm mới

Hàm mới phải có docstring mô tả rõ chức năng, tham số và kết quả trả về.

Ví dụ:

```python
def calculate_weld_width(
    contour: np.ndarray,
    mm_per_pixel: float
) -> float:
    """
    Tính toán bề rộng mối hàn thực tế dựa trên đường bao contour
    và tỉ lệ calibration.

    Args:
        contour (np.ndarray): Tập hợp các điểm biên của mối hàn (N, 1, 2).
        mm_per_pixel (float): Hệ số quy đổi từ pixel sang milimet.

    Returns:
        float: Bề rộng mối hàn tính bằng mm.
        Trả về 0.0 nếu không tìm thấy contour hợp lệ.
    """
```

### 5.3. Type Hinting

100% hàm mới hoặc hàm được chỉnh sửa phải có đầy đủ Type Hint cho:

* Tham số đầu vào.
* Kiểu dữ liệu trả về.

Sử dụng các kiểu dữ liệu phù hợp như:

`Optional`, `Union`, `List`, `Dict`, `Tuple`, `Any`, `np.ndarray`.

Ví dụ:

```python
def detect_anomaly(
    image: np.ndarray,
    threshold: float = 0.5
) -> Tuple[bool, List[Dict[str, Any]]]:
    ...
```

Không khai báo kiểu dữ liệu không chính xác chỉ để đáp ứng hình thức Type Hint.

### 5.4. Tổ chức code

* Ưu tiên cấu trúc module và class hiện hữu.
* Không tạo logic trùng lặp khi đã có hàm xử lý tương đương.
* Tách biệt trách nhiệm giữa Router, Service, Pipeline, Repository và các thành phần liên quan theo kiến trúc hiện tại.
* Không tự ý thêm thư viện hoặc dependency nếu chưa xác định được sự cần thiết và khả năng tương thích.
* Không thay đổi phiên bản thư viện đang sử dụng nếu không thuộc phạm vi yêu cầu.

---

## 6. Xử lý ngoại lệ và bảo vệ luồng (Exception Handling)

### 6.1. Nguyên tắc chung

* TUYỆT ĐỐI KHÔNG sử dụng `except: pass`.
* Không bắt lỗi rồi bỏ qua mà không ghi nhận hoặc xử lý.
* Không sử dụng giá trị mặc định để che giấu lỗi thuật toán, lỗi dữ liệu hoặc lỗi phần cứng.
* Phải phân biệt lỗi dữ liệu đầu vào, lỗi nghiệp vụ, lỗi thuật toán và lỗi giao tiếp thiết bị.

### 6.2. Worker và Pipeline

Các hàm chạy trong `threading.Thread` hoặc bên trong ba Stage của Pipeline phải có cơ chế xử lý ngoại lệ phù hợp.

Ví dụ:

```python
try:
    # Thực hiện xử lý thuật toán hoặc giao tiếp phần cứng.
    ...
except Exception as e:
    error_msg = (
        f"[LỖI][Transform] "
        f"Thất bại khi phán định ảnh: {str(e)}"
    )

    print(error_msg)

    self.services.queue_log_send_client.put({
        "type": "log_Home",
        "message": error_msg
    })
```
