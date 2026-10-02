# System Roadmap & Technical Backlog

## 1. Mục tiêu Định hướng
Định hình lộ trình phát triển, nâng cấp hiệu năng, mở rộng tính năng và chuẩn hóa chất lượng phần mềm cho toàn bộ hệ thống kiểm tra khuyết tật mối hàn và ngoại quan ống.

---

## 2. Trạng thái các Hạng mục Công việc

### 2.1. Đã Hoàn Thành (Done)
- [x] **Core Architecture Refactoring**: Tách biệt rõ ràng các tầng Container, Pipeline, Stages, Judgers và Repositories.
- [x] **AI Model Integration**: Tích hợp đồng thời 3 dòng mô hình AI:
  - Ultralytics YOLO (`object_surface_detect.pt`, `model_hole_and_film.pt`).
  - U-Net Segmentation (`weld_seamunet_unet_service.py`) cho biên dạng và trục tâm đường hàn.
  - PatchCore Anomaly Detection (`model_patch_core.py`) phát hiện xước viền và bất thường bề mặt.
- [x] **Master Adjustment Tooling**: Phát triển bộ 12 công cụ cấu hình trực quan trên nền HTML5 Dual-Coordinate Canvas.
- [x] **Bug Fix BUG-SLIT-01**: Khắc phục triệt để lỗi sinh key `"undefined"` trong cấu hình `SlitWeldInspector` ở cả 2 tầng Frontend và Backend Python.
- [x] **Standard Documentation Architecture**: Hoàn tất tài liệu hóa toàn diện hệ thống theo chuẩn `cach_luu_doc.md` trong `.agents/docs/`.

---

### 2.2. Đang Thực hiện (In Progress)
- [ ] **TASK-CV-01: Phân biệt Bọt khí Trong / Ngoài Đường hàn**:
  - Tận dụng `shared_polygons` từ U-Net để kiểm tra Point-in-Polygon với bọt khí YOLO.
  - Phân loại mã lỗi `E-WELD-BUBBLE-IN` và `E-WELD-BUBBLE-OUT`.

---

### 2.3. Hạng mục Ưu tiên Kế tiếp (Short-term Backlog)

#### 1. Graceful Shutdown & Resource Cleanup (`api_shutdown.py`)
- **Vấn đề**: Khi người dùng tắt ứng dụng đột ngột hoặc dừng server, các luồng daemon COM (`SerialRX`, `SerialTX`, `CheckCOM`) và camera stream (`CStDataStream`) có thể không kịp đóng handle, dẫn đến khóa cổng COM hoặc treo camera ở lần khởi động sau.
- **Giải pháp**:
  - Đăng ký hook `atexit` và FastAPI lifecycle event (`lifespan` handler).
  - Triển khai phương thức `dispose()` chuẩn trên `ManagerSerial`, `IAIControl`, và `Camera`.

#### 2. Nâng cao Độ bền Kết nối Phần cứng (Hardware Fault Tolerance)
- Thêm cơ chế Exponential Backoff cho vòng lặp kết nối lại cổng Serial.
- Đặt giới hạn kích thước (queue maxsize) cho `rx_queue` và `tx_queue` để chống tràn RAM khi phần cứng bị nghẽn (backpressure policy).

#### 3. Mở rộng Độ phủ Kiểm thử Tự động (Test Coverage Expansion)
- Bổ sung unit tests cho tất cả 12 detectors trong `app/judger/`.
- Viết integration test mô phỏng quy trình kiểm tra giả lập (Mocking camera frame và IAI movement).

---

### 2.4. Lộ trình Dài hạn (Long-term Evolution)

```
        Quý 4/2026                      Quý 1/2027                      Quý 2/2027
   ┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
   │ Tối ưu Hóa AI     │           │ WebRTC Streaming  │           │ Đa Camera Đồng Bộ │
   │ TensorRT Engine   │ ────────> │ Siêu Độ Trễ Thấp  │ ────────> │ Soi Đồng Thời 2 Mặt│
   │ FP16 Inference    │           │ Thay thế MJPEG    │           │ Mối Hàn Trên/Dưới │
   └───────────────────┘           └───────────────────┘           └───────────────────┘
```

1. **Chuyển đổi TensorRT (FP16/INT8)**:
   - Export các mô hình PyTorch (YOLO, U-Net) sang TensorRT Engine chạy trực tiếp trên GPU NVIDIA, giảm Cycle Time từ ~120ms xuống < 30ms/frame.
2. **WebRTC Ultra-low Latency Video**:
   - Thay thế luồng MJPEG truyền thống bằng WebRTC data channel, giảm độ trễ hiển thị thời gian thực xuống dưới 50ms và tối ưu băng thông mạng nội bộ.
3. **Mở rộng Đa Camera (Multi-camera Inspection)**:
   - Bổ sung camera thứ 2 soi mặt trong hoặc mặt đối diện của ống hàn.
