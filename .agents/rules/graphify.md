---
trigger: always_on
description: Quy định bắt buộc khai thác Graphify để phân tích tác động, đọc code đúng trọng tâm và cập nhật đồ thị.
---

# Quy chế Ứng dụng Graphify & Đọc Sửa Mã Nguồn Trọng Tâm

Nhằm tối ưu hóa chi phí token, chống tràn bộ nhớ ngữ cảnh (Context Window Bloat) và hạn chế tối đa sinh lỗi, Agent tuân thủ nghiêm ngặt quy trình dưới đây:

---

## 1. Nguyên tắc cốt lõi
- **Không đọc tùy tiện cả file lớn**: Tuyệt đối không dùng `view_file` nạp toàn bộ file hàng trăm/hàng nghìn dòng vào context nếu chỉ cần sửa một vài hàm hoặc dòng code.
- **Tận dụng đồ thị tri thức**: Sử dụng dữ liệu phân tích quan hệ tại `graphify-out/` để xác định chính xác Node/Caller/Callee bị ảnh hưởng trước khi chạm vào mã nguồn.

---

## 2. Quy trình TRƯỚC KHI SỬA (Pre-Edit Workflow)

1. **Khoanh vùng tác động qua Graphify**:
   - Tìm kiếm tính năng/lỗi:
     ```powershell
     graphify query "<tính năng hoặc từ khóa>"
     ```
   - Kiểm tra đường dẫn phụ thuộc giữa 2 thành phần:
     ```powershell
     graphify path "<Component_A>" "<Component_B>"
     ```
   - Tra cứu quan hệ của một Node trọng yếu:
     ```powershell
     graphify explain "<Tên_Node_Hoặc_Class>"
     ```
   *(Nếu lệnh `graphify` chưa có trong PATH toàn cục, sử dụng lệnh qua môi trường ảo: `.\venv-project-width-line\Scripts\python.exe -m graphify ...`)*.

2. **Cơ chế Dự phòng (Fallback)**:
   - Đối với các tác vụ sửa đổi UI/CSS đơn giản, tệp cấu hình độc lập, hoặc khi đồ thị chưa sẵn sàng: Cho phép sử dụng `grep_search` kết hợp `view_file` có kiểm soát phạm vi dòng để tránh làm gián đoạn tiến trình.

3. **Đọc mã nguồn có chọn lọc (Targeted Reading)**:
   - Luôn sử dụng `view_file` kèm tham số `StartLine` và `EndLine` giới hạn trong phạm vi block code cần can thiệp.

---

## 3. Quy trình TRONG KHI SỬA (In-Edit Workflow)
- Sử dụng `replace_file_content` hoặc `multi_replace_file_content` với phạm vi dòng chính xác đã khoanh vùng.
- Tuân thủ nguyên tắc kiến trúc (Pipeline 3 giai đoạn, `ServiceContainer`, type hinting, xử lý ngoại lệ) được quy định tại `project_standards.md`.

---

## 4. Quy trình SAU KHI SỬA (Post-Edit Workflow)
Ngay sau khi chỉnh sửa hoặc thêm mới mã nguồn Python:
- Chạy cập nhật đồ thị gia tăng (chỉ phân tích file thay đổi qua AST, 0 token LLM, chạy offline vài giây):
  ```powershell
  graphify update .
  ```
  *(hoặc: `.\venv-project-width-line\Scripts\python.exe -m graphify update .`)*
- Đảm bảo `graphify-out/graph.json` luôn phản ánh đúng cấu trúc thực tế của mã nguồn.
