# Module: Storage & Repositories (Data Persistence Layer)

## 1. Tổng quan
Hệ thống sử dụng cơ chế lưu trữ dữ liệu dạng tệp tin cục bộ (Local JSON Files và Config Files), được tổ chức và quản lý thông qua **Repository Pattern**. Toàn bộ việc đọc, ghi, cập nhật dữ liệu cấu hình máy, cài đặt phán định, thông số camera và lịch sử đếm sản phẩm đều được đóng gói độc lập trong các lớp Repository tại `app/repository/`.

Mô hình này giúp phân tách hoàn toàn tầng nghiệp vụ (Services, Stages, Pipeline) khỏi tầng dữ liệu vật lý (Filesystem), đồng thời cung cấp các cơ chế phòng vệ chống hỏng tệp (Data sanitization, file existence guarantee, defensive defaults).

---

## 2. Danh mục Repositories và Tệp Dữ liệu

| Repository Class | Tệp Lưu Trữ | Trách Nhiệm Nghiệp Vụ |
| :--- | :--- | :--- |
| [`JudmentLawProductRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/judment_law_product_reponsitory.py) | `config_judgment_law.json` | Quản lý quy chuẩn phán định theo cấu trúc 5 tầng: `Product -> Frame -> Point -> Inspector -> Items/Lines`. Tích hợp bộ lọc tự động `clean_undefined_keys`. |
| [`ProductRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/product_repository.py) | `product.json` | Danh mục mã sản phẩm (Product Catalog), CRUD tên sản phẩm, mã định danh, ngày tạo. |
| [`ChooseProductRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/choose_product_repository.py) | `choose_product.json` | Lưu định danh sản phẩm đang được chọn làm việc (Active Workpiece). |
| [`PointRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/point_repository.py) | `point.json` | Danh sách các vị trí cơ khí (mm) tương ứng với từng Frame chụp của sản phẩm để IAI di chuyển tới. |
| [`CalibrationRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/calibration_reponsitory.py) | `calibration.json` | Hệ số tỷ lệ Pixel/mm, ma trận biến đổi affine/homography cho từng Frame của sản phẩm. |
| [`ProductCountRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/product_count_repository.py) | `product_count.json` | Bộ đếm sản lượng vận hành: Số lượng Total, Số lượng OK, Số lượng NG, và Tỷ lệ Đạt (Yield Rate). |
| [`ComRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/com_repository.py) | `config_com.json` | Thông số kết nối cổng COM IAI (Port, Baudrate, Timeout, Parity). |

---

## 3. Cấu trúc Schema Dữ liệu Quy chuẩn Phán định (`config_judgment_law.json`)

Tệp `config_judgment_law.json` là trung tâm dữ liệu kỹ thuật của máy. Cấu trúc lồng ghép phân cấp như sau:

```json
{
  "<product_id>": {
    "<frame_id>": {
      "<point_id>": {
        "SlitWeldInspector": {
          "0": {
            "nameLine": "1",
            "widthMin": 0.1,
            "widthMax": 4.0,
            "xStart": 1314,
            "yStart": 1260,
            "xEnd": 1148,
            "yEnd": 1496,
            "coordinateSpace": "image"
          }
        },
        "AirBubblesInspector": {
          "0": {
            "x": 850,
            "y": 620,
            "width": 300,
            "height": 180,
            "maxAreaAllowed": 15.0,
            "coordinateSpace": "image"
          }
        },
        "MeasureWeldWidthInspector": {
          "0": {
            "nameLine": "Weld_Center",
            "widthMin": 1.2,
            "widthMax": 3.8,
            "xStart": 600,
            "yStart": 500,
            "xEnd": 1400,
            "yEnd": 520,
            "coordinateSpace": "image"
          }
        }
      }
    }
  }
}
```

---

## 4. Cơ chế Đảm bảo Toàn vẹn Dữ liệu (Defensive Persistence)

### 4.1. Cơ chế Tự Động Làm Sạch (Sanitization Filter)
Khi người dùng chỉnh sửa trên giao diện canvas web, nếu client gửi dữ liệu sai định dạng định danh (ví dụ key `"undefined"` do lỗi click chuột hoặc uninitialized state), hàm `clean_undefined_keys` được kích hoạt ở cả 3 điểm chặn:
1. **Lúc Nạp (`_load()`)**: Quét và sửa ngay khi đọc tệp lên RAM, ghi đè lại file nếu phát hiện bất thường.
2. **Lúc Lưu (`save()`)**: Làm sạch toàn bộ dict trước khi serialize thành chuỗi JSON.
3. **Lúc Cập nhật (`update_data()`)**: Hợp nhất giá trị `undefined` vào item hợp lệ (`0`) và xóa vĩnh viễn key rác.

### 4.2. Khởi tạo an toàn (File Existence & Parent Dir Check)
Mọi Repository đều kế thừa mô hình kiểm tra:
```python
def _ensure_file_exists(self) -> None:
    if self.path.exists():
        return
    self.path.parent.mkdir(parents=True, exist_ok=True)
    with open(self.path, "w", encoding="utf-8") as f:
        json.dump({}, f)
```
Điều này đảm bảo khi hệ thống triển khai lần đầu trên môi trường mới (clean deployment), không bao giờ bị văng lỗi `FileNotFoundError` hay thư mục cha chưa tồn tại.
