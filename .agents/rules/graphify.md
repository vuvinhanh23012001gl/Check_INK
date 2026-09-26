---
trigger: always_on
description: Quy định bắt buộc ứng dụng Graphify để tối ưu hóa token, phân tích tác động trước khi sửa và cập nhật đồ thị sau khi code.
---

# Quy định & Chiến lược Ứng dụng Graphify cho AI Agent

Dự án đã tích hợp và xây dựng đồ thị tri thức mã nguồn tại `graphify-out/`. Mọi AI Agent khi làm việc trên codebase này **bắt buộc tuân thủ quy trình dưới đây** nhằm tối ưu hóa chi phí token, chống tràn ngữ cảnh (context window bloat), tránh ảo giác (hallucination) và nâng cao hiệu suất làm việc.

---

## 1. Mục đích: Tại sao Agent phải dùng Graphify để giảm Token?

- **Rủi ro khi không dùng Graphify (Cách truyền thống)**:
  - Khi cần sửa một tính năng, Agent thường dùng `grep_search`, `list_dir` hoặc nạp toàn bộ file `.py` lớn (hàng nghìn dòng) vào bộ nhớ qua `view_file`.
  - Hậu quả: Tiêu tốn từ **30.000 – 100.000+ token** mỗi lượt hỏi, làm đầy bộ nhớ ngữ cảnh (Context Window Bloat), khiến AI dễ bị mất tập trung (Lost in the middle) và đưa ra phán đoán sai lệch.

- **Hiệu quả khi Agent dùng Graphify (Tiết kiệm 80% – 95% Token)**:
  - Graphify hoạt động như một **Bộ nhớ ngoài dài hạn (External Long-term Memory)** của dự án.
  - Thay vì nạp toàn bộ file mã nguồn, Agent chỉ cần truy vấn và nạp một **Scoped Subgraph** (~300 – 1.500 token) chứa đúng các Node (Class, Function, Module) và Edge (lời gọi hàm, dữ liệu truyền nhận, quan hệ phụ thuộc).
  - Giữ cho Context Window luôn tinh gọn, xử lý nhanh hơn và hạn chế tối đa nguy cơ sinh lỗi khi sửa đổi.

---

## 2. Logic TRƯỚC KHI SỬA (Pre-Edit Workflow - Bắt buộc)

Trước khi thực hiện bất kỳ chỉnh sửa hoặc tạo mới file mã nguồn nào, Agent **tuyệt đối không** được mở đọc mã nguồn một cách tùy tiện. Phải thực hiện tuần tự 3 bước sau:

### Bước 2.1: Phân tích tác động & Luồng quan hệ (Impact Analysis qua Graph)
Sử dụng các lệnh Graphify để trích xuất ngữ cảnh hẹp thay vì đọc code thô:
1. **Tìm kiếm tính năng hoặc lỗi cần xử lý**:
   ```powershell
   graphify query "<tính năng, lỗi hoặc câu hỏi cần tìm hiểu>"
   ```
   *Lệnh này dùng thuật toán BFS/DFS trên đồ thị để trả về cây quan hệ tối giản, chỉ tốn vài trăm token thay vì nạp cả module.*

2. **Xác định đường dẫn phụ thuộc giữa 2 thành phần**:
   ```powershell
   graphify path "<Component_A>" "<Component_B>"
   ```
   *Dùng để kiểm tra xem việc sửa Component A có tác động đến Component B hay không (phân tích caller/callee, tránh phá vỡ kiến trúc).*

3. **Tra cứu nhanh ý nghĩa một Node trọng yếu (Class/Function/Module)**:
   ```powershell
   graphify explain "<Tên_Node_Hoặc_Class>"
   ```
   *Nhận bản tóm tắt chức năng và danh sách kết nối của Node mà không cần mở file đọc từng dòng.*

4. **Điều hướng Wiki**: Nếu `graphify-out/wiki/index.md` tồn tại, Agent ưu tiên đọc điều hướng qua wiki thay vì đọc file thô.

### Bước 2.2: Khoanh vùng vị trí can thiệp (Scoping)
Từ kết quả trả về của Graphify, Agent xác định chính xác:
- Tên file đích cần sửa đổi.
- Tên hàm / phương thức / lớp cụ thể cần can thiệp.
- Các phụ thuộc ngược (upstream) và phụ thuộc xuôi (downstream) cần lưu ý.

### Bước 2.3: Đọc mã nguồn có chọn lọc (Targeted Reading)
- Chỉ sử dụng `view_file` với tham số `StartLine` và `EndLine` giới hạn trong phạm vi block code cần sửa (ví dụ: dòng 120 đến 180).
- **Cấm**: Dùng `view_file` nạp toàn bộ file hàng nghìn dòng vào context nếu chỉ sửa một hàm con.

### Bước 2.4: Tường thuật tiến trình thời gian thực (Runtime Narration - Bắt buộc)
Tuân thủ nghiêm ngặt chuẩn tại [project_standards.md](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/.agents/rules/project_standards.md):
- **Trước khi gọi tool**: Thông báo rõ mục tiêu, node sắp truy vấn trên Graphify hoặc file sắp đọc.
- **Sau khi có kết quả**: Tóm tắt ngay phát hiện kỹ thuật (node nào gọi node nào, nguyên nhân gốc rễ ở hàm/CSS/class nào) trước khi thực hiện bước tiếp theo.
- **Trước khi sửa**: Nói rõ file, số dòng, hàm sẽ sửa và lý do.


---

## 3. Logic TRONG KHI SỬA (In-Edit Workflow)

Khi tiến hành sửa code:
- Tuân thủ nghiêm ngặt các quy định tại [project_standards.md](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/.agents/rules/project_standards.md) (Pipeline 3 giai đoạn, ServiceContainer, 100% Type Hinting, chú thích tiếng Việt).
- Chỉ sử dụng `replace_file_content` hoặc `multi_replace_file_content` với phạm vi dòng chính xác đã khoanh vùng.
- Không đọc thêm các file phụ trợ nếu cấu trúc đồ thị đã chứng minh không có liên kết ảnh hưởng.

---

## 4. Logic SAU KHI SỬA & CẬP NHẬT (Post-Edit & Update Workflow - Bắt buộc)

Ngay sau khi chỉnh sửa hoặc thêm mới mã nguồn:

### Bước 4.1: Chạy cập nhật gia tăng đồ thị tri thức
Agent chạy lệnh sau trong terminal:
```powershell
graphify update .
```
*(hoặc qua môi trường ảo: `.\venv-project-width-line\Scripts\python.exe -m graphify update .`)*


### Bước 4.2: Cơ chế tiết kiệm chi phí của `graphify update`
- **Chi phí Token = 0**: Lệnh `update` trên các file mã nguồn chỉ sử dụng bộ phân tích cú pháp tĩnh **AST (Abstract Syntax Tree)**. Hoàn toàn chạy offline cục bộ, **không tốn token LLM, không tốn chi phí API**.
- **Cơ chế so khớp Hash (Manifest)**: Graphify chỉ phân tích lại những file vừa bị thay đổi nội dung, không quét lại toàn bộ dự án -> Thời gian chạy chỉ mất vài giây.
- **Duy trì tính nhất quán**: Đảm bảo `graphify-out/graph.json` luôn phản ánh mã nguồn thực tế mới nhất, giúp các lượt chat tiếp theo của Agent luôn nhận diện đúng cấu trúc code mới mà không bị lỗi thời.

---

## 5. Bảng tổng hợp so sánh mức độ tiêu thụ Token

| Tình huống của Agent | Cách truyền thống (Lãng phí Token) | Cách ứng dụng Graphify (Tối ưu) | Mức tiết kiệm Token |
| :--- | :--- | :--- | :--- |
| **Tìm hiểu kiến trúc một tính năng** | `view_file` toàn bộ 5-10 file mã nguồn (~30.000 - 50.000 tokens) | `graphify query "<tính năng>"` (~500 - 1.000 tokens) | **Giảm ~95%** |
| **Kiểm tra ảnh hưởng giữa 2 module** | `grep_search` regex và đọc từng đoạn code xuất hiện (~15.000 tokens) | `graphify path "<ModuleA>" "<ModuleB>"` (~300 - 500 tokens) | **Giảm ~95%** |
| **Tìm hiểu mục đích 1 Class/Hàm** | Mở đọc cả file chứa class (~5.000 - 10.000 tokens) | `graphify explain "<Class>"` (~200 - 400 tokens) | **Giảm ~90%** |
| **Đọc code để tiến hành sửa** | `view_file` cả file không giới hạn dòng (~10.000 tokens) | `view_file` với `StartLine`/`EndLine` cụ thể (~500 tokens) | **Giảm ~90%** |
| **Sau khi sửa đổi mã nguồn** | Nạp lại các file để kiểm tra lại quan hệ | `graphify update .` (0 token, xử lý AST nội bộ) | **Tiết kiệm 100% (0 token)** |
