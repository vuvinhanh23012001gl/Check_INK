---

name: graphify
description: Cẩm nang sử dụng Graphify để tạo, truy vấn và cập nhật đồ thị tri thức của mã nguồn.
-------------------------------------------------------------------------------------------------

# Workflow: Graphify

Graphify dùng để phân tích cấu trúc mã nguồn và quan hệ giữa các module, class, function và dependency.

## 1. Khi nào sử dụng

### Full Build

Sử dụng khi:

* Bắt đầu project mới.
* Chưa có `graphify-out/`.
* Graph hiện tại bị lỗi hoặc không còn đồng bộ với source code.
* Cần rebuild toàn bộ graph.

### Query

Sử dụng khi cần:

* Tìm function, class hoặc module liên quan.
* Tìm nơi triển khai một feature.
* Tìm code liên quan đến một lỗi hoặc keyword.

### Path

Sử dụng khi cần:

* Phân tích dependency giữa hai thành phần.
* Xác định quan hệ giữa các module.
* Phân tích ảnh hưởng giữa các thành phần.

### Explain

Sử dụng khi cần:

* Hiểu nhanh một Node.
* Xác định vai trò của module, class hoặc function.

### Incremental Update

Sử dụng sau khi source code thay đổi và graph cần được cập nhật.

Ưu tiên `update` thay vì rebuild toàn bộ.

---

## 2. Full Build

Chạy khi cần tạo hoặc tái tạo toàn bộ graph:

```powershell
graphify .
```

Hoặc:

```powershell
.\venv-project-width-line\Scripts\python.exe -m graphify .
```

### Output

```text
graphify-out/
├── graph.html
├── graph.json
└── GRAPH_REPORT.md
```

* `graph.html`: giao diện trực quan hóa graph.
* `graph.json`: dữ liệu Node và Edge.
* `GRAPH_REPORT.md`: báo cáo phân cụm và các module quan trọng.

---

## 3. Query

Tìm kiếm function, class, module hoặc feature:

```powershell
graphify query "<keyword>"
```

Ví dụ:

```powershell
graphify query "draw_segments"
```

```powershell
graphify query "camera"
```

Ưu tiên `query` trước khi đọc nhiều file nếu chưa biết code liên quan nằm ở đâu.

---

## 4. Path

Tìm dependency hoặc đường liên kết giữa hai thành phần:

```powershell
graphify path "<Module_A>" "<Module_B>"
```

Ví dụ:

```powershell
graphify path "CameraService" "DetectionService"
```

Dùng khi cần phân tích:

* Thành phần nào gọi thành phần nào.
* Quan hệ dependency.
* Phạm vi ảnh hưởng khi thay đổi một module.

---

## 5. Explain

Giải thích nhanh một Node:

```powershell
graphify explain "<Node_Name>"
```

Ví dụ:

```powershell
graphify explain "CameraService"
```

Dùng cho:

* Module
* Class
* Function
* Node

---

## 6. Incremental Update

Sau khi sửa hoặc thêm code:

```powershell
graphify update .
```

Hoặc:

```powershell
.\venv-project-width-line\Scripts\python.exe -m graphify update .
```

Ưu tiên `update` khi chỉ có thay đổi một phần source code.

```text
Source Code thay đổi
        ↓
graphify update .
        ↓
Graph được cập nhật
```

---

## 7. Agent Workflow

```text
Bắt đầu project
      ↓
Kiểm tra graphify-out/
      ↓
Chưa có graph?
   ├── Có → graphify .
   └── Không
         ↓
Cần tìm code liên quan?
   ├── Có → graphify query
   └── Không
         ↓
Cần phân tích dependency?
   ├── Có → graphify path
   └── Không
         ↓
Cần hiểu một Node?
   ├── Có → graphify explain
   └── Không
         ↓
Tiếp tục xử lý task
```

Sau khi sửa code:

```text
Sửa code
   ↓
graphify update .
   ↓
Tiếp tục xử lý task
```

---

## 8. Rules

1. Không chạy `graphify .` nếu graph hiện tại vẫn còn sử dụng được.
2. Sau khi sửa code, ưu tiên `graphify update .`.
3. Khi chưa biết code liên quan nằm ở đâu, dùng `graphify query`.
4. Khi cần phân tích dependency, dùng `graphify path`.
5. Khi cần hiểu nhanh một Node, dùng `graphify explain`.
6. Chỉ lấy context cần thiết từ Graphify.
7. Không đọc toàn bộ project nếu Graphify đã cung cấp đủ context.
8. Không sử dụng Graphify cho task không liên quan đến source code hoặc dependency.

---

## 9. Quick Reference

| Mục đích          | Command                      |
| ----------------- | ---------------------------- |
| Tạo toàn bộ graph | `graphify .`                 |
| Tìm kiếm code     | `graphify query "<keyword>"` |
| Tìm dependency    | `graphify path "<A>" "<B>"`  |
| Giải thích Node   | `graphify explain "<Node>"`  |
| Cập nhật graph    | `graphify update .`          |
