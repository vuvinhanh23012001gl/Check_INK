# Kiến Trúc Tổng Thể Hệ Thống (Architecture Overview)

## 1. Sơ đồ kiến trúc phân tầng (Layered Architecture)

Hệ thống được thiết kế theo mô hình Clean Architecture & Dependency Injection, phân tách rõ ràng giữa giao tiếp mạng, xử lý nghiệp vụ, mô hình AI và phần cứng:

```text
┌─────────────────────────────────────────────────────────────────┐
│               Giao diện Web & Socket.IO Client                  │
│       HTML5 Canvas / Vanilla JS / Event-driven Tool UI          │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP REST / WebSocket
┌────────────────────────────────▼────────────────────────────────┐
│               Tầng Router & API (app/routers/)                  │
│   home, software, product, capture, calibration, law_regulation │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Dependency Injection (ServiceContainer)
┌────────────────────────────────▼────────────────────────────────┐
│              Tầng Dịch Vụ Nghiệp Vụ (app/services/)             │
│   ProductService, PointService, JudmentLawProductService, ...   │
├────────────────────────────────┬────────────────────────────────┤
│    Tầng Phán Định (app/judger/)│  Tầng Động Cơ AI (app/engines/)│
│    Weld, Slit, Border, Bubbles │  UNet, YOLO, PatchCore         │
└────────────────────────────────┼────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│         Tầng Thiết Bị & Lưu Trữ (Hardware & Repository)         │
│  Camera (Stapi/Pylon) │ Serial (IAI/MCU) │ JSON Repositories    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Các thành phần lõi (Core Components)

### 2.1. Entry Point & Lifespan (`run.py` & `app/main.py`)
* Ứng dụng chạy trên máy chủ Uvicorn ASGI tại `127.0.0.1:8000`.
* Cơ chế **FastAPI Lifespan Context Manager** kiểm soát toàn bộ vòng đời khởi tạo và dọn dẹp tài nguyên:
  1. Khởi tạo `ServiceContainer` và gắn vào `fastapi_app.state.services`.
  2. Khởi tạo và kích hoạt `Pipeline` luồng nền.
  3. Kích hoạt task bất đồng bộ `log_sender` để liên tục đẩy queue log ra Socket.IO.
  4. Bọc app bằng `socketio.ASGIApp(sio, fastapi_app)`.

### 2.2. Service Container (`app/container.py`)
* Đóng vai trò là **Composition Root** của toàn bộ ứng dụng (áp dụng mẫu thiết kế Inversion of Control - IoC).
* Quản lý vòng đời Singleton của các thành phần nặng:
  * Trọng số mô hình AI (YOLO models, UNet models, PatchCore memory).
  * Bộ điều phối tìm kiếm hiệu chuẩn `CalibSearchCoordinator`.
  * Các hàng đợi điều khiển và hàng đợi log (`QueueManager`).
  * Trạng thái kết nối phần cứng Camera và Serial Port.

### 2.3. Pipeline Đa Luồng (`app/pipeline.py` & `app/stages/`)
* Chạy như một Daemon Thread độc lập, đảm bảo việc giao tiếp phần cứng thời gian thực không làm đơ (block) luồng xử lý web HTTP/WebSocket.
* Luân chuyển giữa các trạng thái:
  * **`Stage 1 (Preprocess)`**: Xóa queue đệm, bắt tay robot ARM, đưa cánh tay về gốc tọa độ máy.
  * **`Stage 2 (Transform)`**: Vận hành theo mô hình Pipelined Producer-Consumer Queue (Producer điều khiển IAI di chuyển/chụp ảnh đưa vào `queue.Queue(maxsize=3)`; Consumer là 1 AI worker chạy song song suy luận `judment.run_summary` và phát Socket.IO tức thì).
  * **`Stage 3 (Export)`**: Xuất kết quả tổng hợp.
* Đồng bộ trạng thái thread-safe bằng `threading.Lock`.

### 2.4. Kết quả và Xử lý Lỗi Chuẩn Hóa (`app/core/result.py`)
* Mọi hàm service và nghiệp vụ quan trọng đều trả về đối tượng `Result`:
  * `Result.Ok(data)`: Thực thi thành công kèm payload dữ liệu.
  * `Result.Fail(error_code_or_message)`: Thất bại có kiểm soát kèm mã lỗi trong `app/core/erro_code.py`.
* Không sử dụng `try: ... except: pass`; mọi ngoại lệ phần cứng và I/O đều được log chi tiết và đóng gói ngữ cảnh rõ ràng.
