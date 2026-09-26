---
name: graphify
description: Quy trình tạo, truy vấn và cập nhật đồ thị tri thức mã nguồn nhằm tối ưu hóa chi phí token cho AI Agent.
---

# Workflow: graphify

Quy trình chuẩn giúp Agent và người dùng quản lý, khai thác đồ thị tri thức mã nguồn hiệu quả, giảm lượng token tiêu thụ và tránh hiện tượng tràn ngữ cảnh:

---

## 1. Khởi tạo / Xây dựng Đồ thị (Full Build)
Chạy khi bắt đầu dự án mới hoặc khi cần tái lập toàn bộ tri thức:
```powershell
graphify .
```
- Tự động phân tích AST các file code (`.py`) hoàn toàn cục bộ, 0 chi phí API.
- Tạo kết quả trực quan tại thư mục `graphify-out/` gồm:
  - `graph.html`: Bản đồ tương tác trên trình duyệt.
  - `graph.json`: Cấu trúc dữ liệu tri thức đầy đủ.
  - `GRAPH_REPORT.md`: Báo cáo phân cụm (community), god nodes và các liên kết quan trọng.

---

## 2. Quy trình Truy vấn Tiết kiệm Token Trước Khi Sửa Code
Trước khi chỉnh sửa bất kỳ module nào, Agent **bắt buộc** tận dụng đồ thị để khoanh vùng thay vì đọc mã nguồn thô:

1. **Truy vấn ngữ cảnh tính năng / lỗi**:
   ```powershell
   graphify query "<tên chức năng hoặc lỗi cần tìm hiểu>"
   ```
2. **Tìm đường dẫn phụ thuộc và phân tích tác động**:
   ```powershell
   graphify path "<Component_A>" "<Component_B>"
   ```
3. **Giải thích nhanh một Node trung tâm**:
   ```powershell
   graphify explain "<Node_Name>"
   ```
4. **Đọc đúng phạm vi dòng**: Sau khi có vị trí chính xác từ Graphify, Agent chỉ mở file bằng `view_file` với `StartLine` và `EndLine` giới hạn trong hàm cần chỉnh sửa.

---

## 3. Quy trình Cập nhật Gia tăng Sau Khi Sửa Code (Incremental Update)
Ngay sau khi Agent hoàn tất chỉnh sửa, tạo file mới hoặc refactor:
```powershell
graphify update .
```
- **Cơ chế**: Dựa trên Hash của Manifest và phân tích AST tĩnh.
- **Tiêu thụ Token**: **0 Token LLM** (Hoàn toàn miễn phí, chạy offline).
- **Thời gian**: Vài giây, chỉ cập nhật các file có sửa đổi.
- **Mục tiêu**: Đảm bảo các lượt truy vấn tiếp theo của Agent luôn có cấu trúc quan hệ mới nhất.

---

*Tham khảo quy định chi tiết tại [graphify.md](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/.agents/rules/graphify.md).*
