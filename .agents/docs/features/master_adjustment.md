# Tính Năng Điều Chỉnh Master (Master Adjustment)

## 1. Khái niệm và mục đích

**Điều chỉnh Master** là chức năng cấu hình chuẩn kiểm tra cho từng sản phẩm (`Product -> Frame -> Point`). Kỹ sư sử dụng giao diện này để thiết lập các ngưỡng kích thước và vùng quan sát ROI, làm cơ sở để thuật toán phán định tự động đánh giá sản phẩm trên dây chuyền đạt (OK) hay lỗi (NG).

Toàn bộ thông số sau khi thiết lập được lưu trữ tập trung tại file [`app/storage/config_judgment_law.json`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/storage/config_judgment_law.json).

---

## 2. Danh mục các công cụ kiểm tra (Inspectors)

| Tên Inspector | Mục đích kiểm tra | Các thông số chính cần cấu hình |
| :--- | :--- | :--- |
| **`MeasurementWeldInspector`** | Đo độ rộng đường hàn tại các vị trí chỉ định. | `name_line`, `level1` -> `level5`, tọa độ đường đo (`xStart`, `yStart`, `xEnd`, `yEnd`), tùy chọn bật kiểm tra bọt khí. |
| **`SlitWeldInspector`** | Đo khoảng cách khe hở giữa 2 mép hàn. | `nameLine`, `widthMin`, `widthMax`, tọa độ line (`xStart`, `yStart`, `xEnd`, `yEnd`). |
| **`BorderFilmInspector`** | Kiểm tra đường viền dán màng phim. | Tọa độ đoạn thẳng biên viền, dung sai độ lệch viền tối đa. |
| **`AirBubblesItemInspector`** | Phát hiện bọt khí / rỗ khí trong lòng mối hàn. | `weld_polygon` (đa giác đường hàn), `weld_center_points` (trục tâm), ngưỡng diện tích bọt khí tối đa cho phép. |
| **`PermeableMembraneInspector`** | Kiểm tra độ che phủ và vị trí màng bán thấm. | Vùng màng thấm bên trong (`inner`) và đường viền mép màng (`border`). |
| **`HoleItemInspector`** | Kiểm tra sự hiện diện và hình dạng lỗ định vị. | Tọa độ tâm, bán kính/kích thước lỗ, dung sai vị trí. |
| **`ScratchedPipeItemInspector`** | Phát hiện vết trầy xước trên thân ống. | Vùng ROI thân ống, ngưỡng phát hiện vết xước bề mặt. |
| **`ForeignObjectInspector`** | Phát hiện dị vật lạ bám dính trên sản phẩm. | Vùng ROI kiểm tra, mô hình PatchCore và ngưỡng khoảng cách anomaly threshold. |
| **`EndChippingInspector`** | Phát hiện mẻ, sứt cạnh tại đầu ống. | Vùng mép đầu ống, mô hình PatchCore chuyên biệt cho khuyết tật mẻ cạnh. |
| **`ArmSensorInspector`** / **`ArmCoverInspector`** | Kiểm tra lắp ráp cảm biến và nắp che cánh tay. | Bounding box vị trí linh kiện (YOLO object detection). |

---

## 3. Quy trình quy đổi tọa độ Canvas và Ảnh Master

Giao diện người dùng vẽ trên thẻ HTML5 Canvas có kích thước hiển thị cố định (ví dụ `1024 x 768`), trong khi ảnh chụp từ camera công nghiệp có độ phân giải gốc là `2048 x 1536`.

```text
Tọa độ Canvas (Web Client)
       │
       ▼ (Gửi API /law_regulation/save kèm kích thước canvas)
Backend: convert_canvas_coordinates()
       │  scale_x = image_width / canvas_width
       │  scale_y = image_height / canvas_height
       ▼
Tọa độ Pixel Ảnh Gốc (Lưu trữ trong config_judgment_law.json)
       │  Đánh dấu: "coordinateSpace": "image"
       ▼
Khi nạp lại giao diện (/law_regulation/):
Frontend: convertStoredImageCoordinatesToCanvas()
       │  scale_x = canvas_width / image_width
       │  scale_y = canvas_height / image_height
       ▼
Hiển thị chính xác vị trí đường vẽ trên Canvas Client
```

> [!IMPORTANT]
> Dữ liệu tọa độ đã quy đổi sang ảnh gốc luôn có trường `"coordinateSpace": "image"`. Backend có cơ chế kiểm tra trường này để tránh lỗi nhân đôi tỷ lệ (double-scaling) khi lưu nhiều lần.
