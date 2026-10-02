# Tổng Quan Hệ Thống Kiểm Tra Chất Lượng (Features Overview)

## 1. Mục đích hệ thống

Hệ thống **Python Detect Width Line** là giải pháp thị giác máy tính công nghiệp (Machine Vision Inspection) chuyên dụng, được triển khai trên dây chuyền sản xuất tự động nhằm:

* **Đo kích thước hình học chính xác:** Đo độ rộng mối hàn (`MeasurementWeldInspector`), khoảng cách khe hở đường hàn (`SlitWeldInspector`).
* **Kiểm tra ngoại quan và cấu trúc:** Nhận diện vị trí lỗ (`HoleItemInspector`), nắp cánh tay robot (`ArmCoverInspector`), cảm biến vị trí (`ArmSensorInspector`).
* **Phát hiện dị tật và khuyết tật bề mặt:** Phát hiện bọt khí đường hàn (`AirBubblesItemInspector`), xước ống (`ScratchedPipeItemInspector`), mẻ đầu ống (`EndChippingInspector`), dị vật bất thường (`ForeignObjectInspector`).
* **Kiểm tra màng và viền dán:** Nhận diện đường viền màng phim (`BorderFilmInspector`), màng thẩm thấu bên trong và đường viền bao ngoài (`PermeableMembraneInspector`).

---

## 2. Quy trình vận hành kiểm tra (Inspection Workflow)

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Công nhân / Kỹ sư
    participant UI as Giao diện Web Client
    participant Server as Backend FastAPI & Container
    participant ARM as Cánh tay IAI / MCU (Serial)
    participant Camera as Camera Công Nghiệp (Stapi/Pylon)
    participant AI as Pipeline AI Vision & Judger

    Operator->>UI: Chọn sản phẩm (Product) & bắt đầu kiểm tra
    UI->>Server: Kích hoạt Pipeline kiểm tra tự động
    Server->>ARM: Gửi lệnh di chuyển cánh tay tới toạ độ điểm (XYZ)
    ARM-->>Server: Phản hồi hoàn thành di chuyển (Handshake)
    Server->>Camera: Phát lệnh Trigger chụp ảnh
    Camera-->>Server: Trả về ảnh gốc (2048 x 1536)
    Server->>AI: Chạy mô hình (YOLO / UNet / PatchCore) & Thuật toán trích xuất
    AI-->>Server: Tọa độ, độ rộng, diện tích, đa giác khuyết tật
    Server->>Server: Đối chiếu luật Master trong config_judgment_law.json -> Phán định OK / NG
    Server-->>UI: Hiển thị kết quả, vẽ bounding box, đường đo & Socket.IO realtime log
    Server->>Server: Lưu ảnh kết quả và ghi nhật ký xuất xưởng (log_csv, log_img)
```

---

## 3. Các chế độ hoạt động chính

### 3.1. Chế độ Vận hành Tự động (Run Inspection)
* Hệ thống tự động di chuyển robot qua toàn bộ các Frame và Point của Model đang chọn.
* Tự động chụp ảnh, xử lý inference AI và đưa ra phán định OK / NG tổng thể cho toàn bộ sản phẩm.

### 3.2. Chế độ Điều chỉnh Master (Master Adjustment)
* Dành cho kỹ sư thiết lập chuẩn mẫu cho từng loại sản phẩm.
* Cho phép vẽ và cấu hình thông số tiêu chuẩn:
  * Dung sai tối thiểu / tối đa (Min / Max width).
  * Các ngưỡng Level phán định (Level 1 -> 5).
  * Vùng kiểm tra bọt khí, dị vật, vết trầy xước.
* Quy đổi tọa độ trực tiếp giữa màn hình Canvas và toạ độ ảnh vật lý `(coordinateSpace: image)`.

### 3.3. Chế độ Hiệu chuẩn kích thước (Calibration)
* Tự động hoặc thủ công quy đổi hệ số tỷ lệ giữa pixel ảnh camera và kích thước milimet vật lý ngoài thực tế (`scaleX`, `scaleY`, mm/pixel).
* Đồng bộ độ biến dạng hoặc khoảng cách tiêu cự camera.
