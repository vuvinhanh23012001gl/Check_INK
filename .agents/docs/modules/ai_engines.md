# Kiến Trúc Các Động Cơ AI (AI Engines)

## 1. Cấu trúc tổ chức thư mục `app/engines/`

Thư mục `app/engines/` chia thành 3 lớp phân cấp chặt chẽ:

```text
app/engines/
├── model_AI/             # Lớp bọc thấp nhất: Nạp trọng số và thực thi forward/inference
│   ├── model_yolo_object.py     # Ultralytics YOLO Object Detection
│   ├── model_yolo_segment.py    # Ultralytics YOLO Instance Segmentation
│   ├── model_unet.py            # PyTorch UNet (Detect đường hàn và viền film)
│   └── model_patch_core.py      # PatchCore Anomaly Detection (FAISS index + CNN backbone)
├── AI_model_process/     # Lớp xử lý dữ liệu: Biến đổi Tensor/Mask -> Toạ độ, Contours, Polygons
│   ├── frame_yolo_object_process.py
│   └── frame_yolo_segment_process.py
└── service/              # Lớp dịch vụ nghiệp vụ: Cung cấp API trực tiếp cho Judger & Router
    ├── structure_frame_yolo_service.py   # Nhận diện cấu trúc (Hole, Arm Cover, Arm Sensor)
    ├── surface_fram_yolo_service.py     # Nhận diện bề mặt (Khuyết tật bọt khí, vết xước)
    ├── boder_film_unet_service.py       # Phân đoạn và nhận diện đường viền màng phim
    ├── permeable_membrane_yolo_service.py# Phân đoạn màng thấm trong & viền ngoài
    └── weld_seamunet_unet_service.py    # Phân đoạn đường hàn và trích xuất đa giác
```

---

## 2. Chi tiết các mô hình AI

### 2.1. UNet Segmentation Models
* **Đường hàn (`PATH_FILE_UNET_DETECT_WELD_LINE`):** Phân đoạn vùng nóng chảy của mối hàn. Đầu ra được xử lý qua thuật toán tìm đường biên (`cv2.findContours`) để trích xuất đa giác bao kín và đường trục tâm (skeleton).
* **Viền Film (`PATH_FILE_UNET_DETECT_FILM_BORDER_LINE`):** Phân đoạn đường ranh giới của tấm màng dán, phục vụ việc đo độ lệch mép và độ thẳng của viền.

### 2.2. YOLO Models (Ultralytics)
* **Cấu trúc (`PATH_FILE_MODEL_YOLO_STRUCTURE`):** Phát hiện 3 lớp đối tượng: `hole` (lỗ), `cover_arm` (nắp tay kẹp), `sensor_arm` (cảm biến).
* **Bề mặt (`PATH_FILE_MODEL_YOLO_SURFACE`):** Phân đoạn các lỗi: `air_bubble` (bọt khí), `scratch` (vết xước).
* **Màng bán thấm (`PATH_FILE_MODEL_YOLO_PERMEABLE_MEMBRANE_*`):** Hai mô hình riêng biệt nhận diện màng bên trong và đường viền bao quanh màng.

### 2.3. PatchCore Anomaly Detection
* Ứng dụng cho bài toán phát hiện dị tật không có mẫu lỗi cố định: **Dị vật bất thường (`ForeignObjectInspector`)** và **Mẻ đầu ống (`EndChippingInspector`)**.
* Sử dụng trích xuất đặc trưng (Feature Extractor) kết hợp cơ sở dữ liệu nhớ lân cận (Nearest-Neighbor Coreset / FAISS index).
* So sánh khoảng cách dị tật với ngưỡng `anomaly_threshold` để kết luận bất thường mà không cần dán nhãn lỗi từ trước.

---

## 3. Quản lý tài nguyên & Hiệu năng (Performance & VRAM)

* **Khởi tạo 1 lần (Singleton in Container):** Toàn bộ mô hình được nạp một lần duy nhất vào VRAM/RAM khi khởi động container trong `app/container.py`. Tuyệt đối không tải lại model trên mỗi request.
* **Warmup khi Startup:** Các mô hình thực hiện inference thử một tensor rỗng (dummy input) ngay khi bật server để tránh độ trễ (latency spike) ở lần kiểm tra đầu tiên.
* **Xử lý Thread-safe & Batch:** Vì PyTorch và OpenCV chia sẻ tài nguyên tính toán, các lời gọi từ API async được bọc qua `asyncio.to_thread` để tránh khóa giữ Event Loop chính của FastAPI.
