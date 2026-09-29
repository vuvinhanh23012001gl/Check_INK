---
trigger: always_on
description: Quy định bắt buộc khai thác Graphify để phân tích tác động, đọc code đúng trọng tâm và cập nhật đồ thị.
---

# Quy chế sử dụng Graphify và đọc/sửa mã nguồn trọng tâm

## 1. Mục tiêu và nguyên tắc cốt lõi

Quy chế này nhằm tối ưu hóa việc sử dụng context window, giảm lượng token tiêu thụ, hạn chế đọc mã nguồn không cần thiết và giảm nguy cơ phát sinh lỗi khi Agent chỉnh sửa dự án.

### 1.1. Nguyên tắc bắt buộc

* Ưu tiên sử dụng Graphify để xác định kiến trúc, quan hệ giữa các thành phần và phạm vi ảnh hưởng trước khi sửa code.
* Không đọc toàn bộ file lớn nếu chỉ cần kiểm tra hoặc chỉnh sửa một hàm, class hoặc đoạn code cụ thể.
* Không dựa hoàn toàn vào đồ thị để kết luận logic thực tế của chương trình.
* Luôn xác minh code nguồn tại vị trí cần sửa trước khi thực hiện thay đổi.
* Không sử dụng đồ thị đã lỗi thời như thể nó phản ánh chính xác trạng thái hiện tại của mã nguồn.
* Ưu tiên thay đổi tối thiểu, đúng phạm vi yêu cầu và bảo toàn hành vi hiện hữu.

---

## 2. Quy trình trước khi sửa code (Pre-Edit Workflow)

### 2.1. Kiểm tra trạng thái Graphify

Trước khi truy vấn đồ thị, kiểm tra sự tồn tại của:

```text
graphify-out/graph.json
```

Nếu chưa có đồ thị:

* Thực hiện xây dựng đồ thị theo hướng dẫn của Graphify.
* Không giả định rằng đồ thị đã tồn tại hoặc đã được cập nhật.

Nếu đồ thị có thể đã lỗi thời:

* Ưu tiên cập nhật đồ thị trước khi sử dụng kết quả để xác định phạm vi ảnh hưởng.
* Nếu không thể cập nhật, phải ghi nhận giới hạn này và xác minh quan hệ bằng mã nguồn thực tế.

### 2.2. Truy vấn đồ thị để khoanh vùng tác động

Ưu tiên sử dụng các lệnh sau:

**Tìm kiếm chức năng hoặc luồng xử lý:**

```powershell
graphify query "Mô tả chức năng hoặc từ khóa cần tìm"
```

**Tìm đường liên kết giữa hai thành phần:**

```powershell
graphify path "Component_A" "Component_B"
```

**Phân tích quan hệ của một Node:**

```powershell
graphify explain "Tên_Node_Hoặc_Class"
```

Mục đích:

* Xác định file chứa chức năng cần sửa.
* Xác định Caller và Callee liên quan.
* Xác định các module có khả năng bị ảnh hưởng.
* Tìm đường đi của dữ liệu giữa các thành phần.
* Hạn chế việc tìm kiếm và đọc code không liên quan.

Không bắt buộc sử dụng cả ba lệnh cho mọi tác vụ. Chọn lệnh phù hợp với câu hỏi kỹ thuật cần giải quyết.

### 2.3. Cơ chế dự phòng khi Graphify không khả dụng

Cho phép sử dụng tìm kiếm văn bản và đọc code trực tiếp trong các trường hợp:

* Graphify chưa được cài đặt hoặc chưa khởi tạo.
* Đồ thị chưa có dữ liệu của module cần kiểm tra.
* Tác vụ chỉnh sửa UI/CSS hoặc file cấu hình độc lập.
* Cần xác minh một đoạn code cụ thể.
* Kết quả truy vấn đồ thị không đủ để xác định chính xác vị trí cần sửa.

Không được trì hoãn một tác vụ đơn giản chỉ để bắt buộc sử dụng Graphify.

### 2.4. Đọc mã nguồn có chọn lọc (Targeted Reading)

Sau khi xác định được vị trí cần kiểm tra:

* Sử dụng `view_file` với `StartLine` và `EndLine` nếu công cụ hỗ trợ.
* Chỉ đọc phạm vi chứa hàm, class hoặc đoạn logic liên quan.
* Mở rộng phạm vi đọc khi cần hiểu đầy đủ điều kiện đầu vào, đầu ra hoặc luồng xử lý.
* Kiểm tra các hàm gọi trực tiếp và các hàm được gọi nếu chúng ảnh hưởng đến hành vi cần sửa.
* Không đọc toàn bộ file hàng trăm hoặc hàng nghìn dòng chỉ để chỉnh sửa một vài dòng code.

Nếu công cụ không hỗ trợ đọc theo dòng, sử dụng phương thức tương đương để giới hạn nội dung trả về.

### 2.5. Xác minh trước khi sửa

Trước khi chỉnh sửa, phải xác định:

1. File và hàm cần thay đổi.
2. Vị trí gọi hàm và các thành phần phụ thuộc.
3. Dữ liệu đầu vào và đầu ra liên quan.
4. Hành vi hiện hữu cần bảo toàn.
5. Phạm vi ảnh hưởng có thể phát sinh.

Nếu thông tin chưa rõ hoặc có nhiều cách hiểu, tuân thủ quy định Requirement Clarification trong `project_standards.md` và hỏi người dùng trước khi triển khai.

---

## 3. Quy trình trong khi sửa code (In-Edit Workflow)

### 3.1. Giới hạn phạm vi chỉnh sửa

Ưu tiên sử dụng:

* `replace_file_content`
* `multi_replace_file_content`

Hoặc công cụ chỉnh sửa tương đương có khả năng giới hạn phạm vi thay đổi.

Quy định:

* Chỉ thay đổi đoạn code cần thiết.
* Không ghi đè toàn bộ file nếu chỉ cần sửa một hàm.
* Không tự ý refactor các module không liên quan.
* Không xóa code cũ khi chưa xác định được tác động.
* Không tự ý thay đổi API, cấu trúc dữ liệu hoặc giao thức phần cứng.

### 3.2. Tuân thủ quy chuẩn dự án

Mọi thay đổi phải tuân thủ `project_standards.md`, bao gồm:

* Pipeline 3 giai đoạn.
* ServiceContainer.
* Type Hinting và Docstring.
* Exception Handling.
* Logging Realtime.
* Quy tắc OK/NG.
* An toàn giao tiếp STM32/IAI.
* Nguyên tắc làm rõ yêu cầu trước khi triển khai.

### 3.3. Không sửa dựa trên suy đoán từ đồ thị

Graphify chỉ được sử dụng để định hướng việc đọc và xác định quan hệ.

Trước khi sửa, Agent phải xác minh logic thực tế trong code nguồn, không tự suy diễn hành vi chương trình chỉ từ tên Node, tên hàm hoặc quan hệ trên đồ thị.

---

## 4. Quy trình sau khi sửa code (Post-Edit Workflow)

### 4.1. Kiểm tra thay đổi

Sau khi chỉnh sửa:

1. Kiểm tra Git Diff để xác định các thay đổi thực tế.
2. Kiểm tra cú pháp và lỗi import nếu phù hợp.
3. Kiểm tra các hàm hoặc module liên quan trực tiếp.
4. Kiểm tra các hành vi hiện hữu cần bảo toàn.
5. Chạy kiểm thử phù hợp với phạm vi thay đổi.

Không tuyên bố kiểm thử thành công nếu chưa thực sự thực hiện kiểm thử.

### 4.2. Cập nhật Graphify

Ngay sau khi hoàn tất thay đổi mã nguồn, thực hiện cập nhật đồ thị:

```powershell
graphify update .
```

Nếu Graphify được cài đặt trong môi trường ảo và không có trong PATH:

```powershell
.\venv-project-width-line\Scripts\python.exe -m graphify update .
```

Lưu ý: Chỉ sử dụng cú pháp chạy module nếu môi trường cài đặt Graphify hỗ trợ entry point này.

### 4.3. Xác minh kết quả cập nhật

Sau khi chạy lệnh:

* Kiểm tra mã thoát và thông báo kết quả.
* Xác nhận `graphify-out/graph.json` tồn tại.
* Nếu có lỗi, ghi nhận nguyên nhân và thông báo cho người dùng.
* Không tuyên bố đồ thị đã đồng bộ nếu quá trình cập nhật thất bại.
* Không sử dụng kết quả đồ thị cũ để khẳng định quan hệ code mới đã được cập nhật.

### 4.4. Đồng bộ đồ thị với mã nguồn

Mục tiêu là duy trì:

```text
Source Code
    ↓
Graphify Update
    ↓
graphify-out/graph.json
```

Đồ thị phải được cập nhật sau các thay đổi mã nguồn có ảnh hưởng đến cấu trúc hoặc quan hệ giữa các thành phần.

Đối với thay đổi chỉ liên quan đến comment hoặc định dạng, Agent có thể đánh giá mức độ cần thiết của việc cập nhật theo khả năng phát hiện thay đổi của Graphify.

---

## 5. Quy định tối ưu Context Window

### 5.1. Ưu tiên thông tin có giá trị cao

Thứ tự ưu tiên khi thu thập thông tin:

1. Kết quả Graphify liên quan trực tiếp đến yêu cầu.
2. Đoạn code tại vị trí cần sửa.
3. Các hàm gọi trực tiếp hoặc được gọi trực tiếp.
4. Cấu hình và dữ liệu ảnh hưởng đến chức năng.
5. Các module liên quan gián tiếp khi thực sự cần thiết.

### 5.2. Hạn chế nạp dữ liệu không cần thiết

* Không đọc toàn bộ file lớn chỉ để tìm một hàm.
* Không lặp lại việc đọc cùng một đoạn code nếu nội dung chưa thay đổi.
* Không nạp toàn bộ `GRAPH_REPORT.md` khi chỉ cần thông tin của một Node.
* Không truy vấn nhiều lần cùng một nội dung nếu kết quả trước đó vẫn còn phù hợp.
* Ưu tiên kết quả truy vấn có phạm vi hẹp và đủ trả lời câu hỏi kỹ thuật.

### 5.3. Không đánh đổi độ chính xác để giảm token

Việc tối ưu token không được làm giảm độ chính xác của việc sửa code.

Nếu cần đọc thêm code để xác minh:

* Được phép mở rộng phạm vi đọc.
* Ưu tiên đọc đúng module liên quan thay vì suy đoán.
* Không bỏ qua bước xác minh chỉ để tiết kiệm context.

---

## 6. Quy trình báo cáo

Sau khi hoàn tất tác vụ, Agent phải báo cáo ngắn gọn:

* Các file đã đọc và chỉnh sửa.
* Các Node hoặc quan hệ quan trọng được sử dụng để xác định phạm vi tác động.
* Nội dung thay đổi chính.
* Kết quả kiểm thử.
* Trạng thái cập nhật Graphify.
* Những vấn đề chưa được xác minh.

Không khẳng định Graphify đã đồng bộ, kiểm thử đã thành công hoặc không có ảnh hưởng ngoài phạm vi nếu chưa có căn cứ xác minh.
