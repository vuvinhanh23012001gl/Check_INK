# Module: Frontend Architecture (Web UI & Canvas Interaction)

## 1. Tổng quan Kiến trúc Giao diện
Giao diện người dùng được xây dựng theo kiến trúc Web SPA/MPA nhẹ trên nền HTML5 Canvas, Vanilla JavaScript ES6+, Bootstrap/Custom CSS, và Socket.IO client.
Hệ thống không sử dụng các framework nặng (như React hay Angular) để tối đa hóa tốc độ nạp trang và giảm độ trễ render trên màn hình công nghiệp IPC cảm ứng.

Hệ thống frontend chia làm 4 phân tầng chính:
1. **Canvas Drawing & Interaction Layer** (`app/static/js/canvas/`): Quản lý sự kiện chuột/cảm ứng, vẽ hình chiếu, scale tọa độ màn hình sang ảnh gốc.
2. **Inspector Tool Modules** (`app/static/js/tool/`): Logic nghiệp vụ cho từng công cụ kiểm tra (Slit, Bubbles, Weld Width, Chipping, v.v.).
3. **Domain Models & Services** (`app/static/js/model/`, `app/static/js/services/`): Quản lý trạng thái thực thể, chuyển đổi Dictionary sang Object và ngược lại.
4. **Coordination & Page Controllers** (`app/static/js/home.js`, `capture_frame.js`, `dimetional_calibration.js`): Điều phối các panel, gọi REST API và lắng nghe sự kiện WebSocket.

---

## 2. Canvas Layer & Hệ Tọa Độ Kép (Dual-Coordinate Transform)

### 2.1. Phân tách Canvas chuyên biệt
- **`LineDrawerCanvas`** ([`line_drawer_canvas.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/canvas/line_drawer_canvas.js)): Chuyên trách vẽ và tương tác với các đối tượng hình học dạng đoạn thẳng (Line, Slit, Line Width).
- **`RectangleDrawerCanvas`** ([`rectangel_drawer_canvas.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/canvas/rectangel_drawer_canvas.js)): Chuyên trách vẽ vùng quan tâm ROI chữ nhật (Bounding Box, Defect ROI, Bubble Inspection Area).
- **`DimensionalCalibrationCanvas`** ([`dimesional_calibration_canvas.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/canvas/dimesional_calibration_canvas.js)): Canvas phục vụ căn chỉnh kích thước, đo khoảng cách chuẩn (mm) để tính tỉ lệ pixel.

### 2.2. Biến đổi Tọa độ Hiển thị ↔ Tọa độ Ảnh Gốc
Ảnh công nghiệp có độ phân giải lớn (thường từ 2000px đến 5000px), trong khi Canvas hiển thị trên màn hình bị giới hạn kích thước vật lý (VD: 800x600px).
Do đó, Canvas Controller luôn áp dụng công thức tỉ lệ 2 chiều:

```javascript
// Khi người dùng click vẽ trên Canvas màn hình:
imageX = Math.round(canvasX * (originalImageWidth / canvasDisplayWidth));
imageY = Math.round(canvasY * (originalImageHeight / canvasDisplayHeight));

// Khi nạp cấu hình từ DB lên vẽ lại trên Canvas:
canvasX = Math.round(imageX * (canvasDisplayWidth / originalImageWidth));
canvasY = Math.round(imageY * (canvasDisplayHeight / originalImageHeight));
```

Mọi dữ liệu lưu trong `config_judgment_law.json` luôn được chuẩn hóa theo **Image Coordinate Space** (`coordinateSpace: "image"`), giúp thông số kiểm tra hoàn toàn độc lập với kích thước hiển thị của màn hình người dùng.

---

## 3. Vòng đời Công cụ Kiểm tra (Tool & Inspector Lifecycle)

Mỗi công cụ đo đạc tuân thủ mẫu thiết kế Controller-Service-Model:

```
[Tool Controller] (VD: slit_tool.js)
       │  - Bắt sự kiện click Canvas
       │  - Mở/đóng popup thông số (WidthMin, WidthMax)
       ▼
[Inspector Service] (VD: slit_item_inspector.js)
       │  - Quản lý danh sách đối tượng: this.slits = {}
       │  - addSlit(), updateSlit(), removeSlit()
       │  - fromDict(jsonDict) & toDict()
       ▼
[Entity Model] (VD: model_slit.js)
          - id_line, nameLine, widthMin, widthMax
          - xStart, yStart, xEnd, yEnd
```

### Quy trình Sửa chữa và Nạp lại Đối tượng:
1. Người dùng click vào một đường vẽ đã tồn tại trên Canvas.
2. `LineDrawerCanvas` phát hiện click trúng tọa độ gần đường thẳng (khoảng cách Euclidean d < tolerance).
3. Gọi callback `func_callback_click_on_line_drawn(lineData)`.
4. Tool lấy định danh `lineData.id_line`, nạp dữ liệu cũ vào form modal.
5. Khi người dùng bấm "Lưu", Inspector Service cập nhật chính xác item có `id_line` tương ứng (tránh tạo thêm item mới hoặc sinh key `undefined`).

---

## 4. Giao tiếp Thời gian thực (Real-time Socket.IO & REST API)

- **REST API Endpoints**:
  - `/law_regulation/`: Lấy quy chuẩn phán định.
  - `/law_regulation/save`: Lưu quy chuẩn.
  - `/product/all`: Lấy danh sách sản phẩm.
  - `/camera/capture`: Kích hoạt chụp ảnh thủ công.
  - `/dimensional_calibration/calculate`: Tính toán căn chuẩn mm/pixel.
- **Socket.IO Event Stream**:
  - `status_machine`: Cập nhật trạng thái IAI (Origin, Running, Pause, Error).
  - `inspection_result`: Đẩy kết quả phán định (OK/NG, thời gian xử lý, kích thước đo) ngay khi Pipeline hoàn tất frame.
  - `log_message`: Nhật ký hoạt động hiển thị lên bảng điều khiển Console trên UI.
