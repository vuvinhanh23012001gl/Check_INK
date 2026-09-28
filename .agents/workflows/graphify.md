---
name: graphify
description: Cẩm nang lệnh thực thi quản trị và khai thác đồ thị tri thức mã nguồn Graphify.
---

# Workflow: graphify

Cẩm nang lệnh nhanh để khởi tạo, truy vấn và cập nhật đồ thị tri thức mã nguồn:

---

## 1. Khởi tạo toàn diện (Full Build)
Chạy khi bắt đầu dự án hoặc khi cần tái lập toàn bộ đồ thị tri thức:
```powershell
graphify .
```
*(Hoặc qua venv: `.\venv-project-width-line\Scripts\python.exe -m graphify .`)*

Dữ liệu đầu ra tại `graphify-out/`:
- `graph.html`: Giao diện trực quan hóa tương tác trên trình duyệt.
- `graph.json`: Cấu trúc dữ liệu Node và Edge.
- `GRAPH_REPORT.md`: Tóm tắt phân cụm và các module trọng yếu.

---

## 2. Tra cứu & Phân tích tác động (Impact Analysis)

1. **Tìm kiếm tính năng / module / lỗi**:
   ```powershell
   graphify query "<từ khóa hoặc hàm cần tìm>"
   ```
2. **Tìm đường dẫn phụ thuộc giữa 2 thành phần**:
   ```powershell
   graphify path "<Module_A>" "<Module_B>"
   ```
3. **Giải thích tóm tắt một Node (Class/Function)**:
   ```powershell
   graphify explain "<Tên_Node>"
   ```

---

## 3. Cập nhật gia tăng sau khi code (Incremental Update)
Chạy ngay sau khi sửa code (chạy offline qua AST, 0 token API):
```powershell
graphify update .
```
*(Hoặc qua venv: `.\venv-project-width-line\Scripts\python.exe -m graphify update .`)*
