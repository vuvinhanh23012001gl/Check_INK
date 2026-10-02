# Tính Năng Quản Lý Sản Phẩm & Điểm Kiểm Tra (Product Management)

## 1. Cấu trúc dữ liệu phân cấp 3 tầng

Hệ thống tổ chức dữ liệu sản xuất theo cấu trúc cây 3 tầng chặt chẽ:

$$\text{Product (Sản phẩm)} \longrightarrow \text{Frame (Khung chụp/Vị trí góc)} \longrightarrow \text{Point (Điểm kiểm tra chi tiết)}$$

```text
Product (Mã định danh sản phẩm, ví dụ: "1", "2")
  │
  ├── Frame 0 (Khung kẹp / góc chụp đầu tiên)
  │     ├── Point 0 (Điểm đo khe hàn) -> Tọa độ ARM (X, Y, Z) + Ảnh Master
  │     ├── Point 1 (Điểm đo độ rộng đường hàn)
  │     └── Point 2 (Điểm kiểm tra màng bán thấm)
  │
  └── Frame 1 (Khung kẹp thứ hai nếu có)
        └── Point 0 ...
```

---

## 2. Quản lý sản phẩm (Products)

* **Danh mục sản phẩm (`app/storage/products.json`):** Lưu trữ danh sách các sản phẩm hỗ trợ kiểm tra trên chuyền kèm tên hiển thị, mã SKU và thời gian tạo.
* **Sản phẩm đang chọn (`app/storage/choose_product.json`):** Xác định sản phẩm mục tiêu hiện thời. Mọi thao tác từ nạp ảnh, kiểm tra tự động đến nạp luật Master đều dựa trên ID của sản phẩm đang chọn này.
* **Tạo mới sản phẩm:** Khi tạo sản phẩm mới, hệ thống tự động sinh cấu trúc thư mục lưu ảnh master `app/storage/img_points/<product_id>/` và khởi tạo node rỗng trong cây điểm và cây luật.
* **Xóa sản phẩm:** Khi xóa một sản phẩm, dịch vụ `JudmentLawProductService.delete_product_data()` sẽ dọn dẹp đồng bộ:
  * Node cấu hình luật trong `config_judgment_law.json`.
  * Dữ liệu huấn luyện và model PatchCore tương ứng trong `app/storage/img_coordinate_output/<product_id>/`.
  * Dữ liệu tham chiếu đường hàn `weld_reference` trên ổ đĩa.
  * Thư mục ảnh điểm kiểm tra.

---

## 3. Quản lý điểm kiểm tra (Points & Frames)

* **Cây điểm (`app/storage/points.json`):** Lưu trữ danh sách điểm kiểm tra cho từng sản phẩm. Mỗi điểm gắn với:
  * Tọa độ không gian 3 chiều thực tế của cánh tay robot: `x`, `y`, `z` (và tốc độ di chuyển `speed`).
  * Tên gọi định danh của điểm kiểm tra.
* **Ảnh Master chuẩn:**
  * Mỗi Point có một ảnh mẫu chuẩn được lưu tại `app/storage/img_points/<product_id>/<frame_id>/<point_id>.jpg`.
  * Ảnh này được dùng để kỹ sư vẽ luật Master (vẽ đường đo, khoanh vùng dị tật) và dùng để đối chiếu khi chạy kiểm tra.
* **Đồng bộ tự động giữa Point và Law:** Khi mở màn hình Master (`/law_regulation/`), hệ thống tự động đối chiếu các Frame/Point từ `points.json` sang `config_judgment_law.json`, tự động bù đắp các node còn thiếu để người dùng có thể cấu hình ngay.
