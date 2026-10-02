# Tầng Phán Định Quy Chuẩn (Judger Detectors)

## 1. Vai trò của tầng Judger

Tầng Judger (`app/judger/`) là thành phần quyết định chất lượng của hệ thống. Nó tiếp nhận đầu ra trích xuất từ các Động cơ AI (tọa độ box, mặt nạ phân đoạn, bản đồ nhiệt dị tật) và đối chiếu với **Bộ luật Master** được lưu trong [`config_judgment_law.json`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/storage/config_judgment_law.json) để đưa ra kết luận:
* **`OK`**: Sản phẩm đạt chuẩn theo thông số Master.
* **`NG`**: Sản phẩm lỗi, kèm thông tin chi tiết về vị trí, giá trị đo và lý do vi phạm.

---

## 2. Danh sách các Detectors chính

```text
app/judger/
├── weld_seam_air_bubbles_detector.py  # Phán định bọt khí đường hàn
├── border_detector.py                 # Phán định đường biên viền Film
├── hole_detector.py                   # Phán định vị trí và hình học lỗ
├── arm_cover_detector.py              # Phán định nắp che cánh tay robot
├── arm_sensor_detector.py             # Phán định cảm biến vị trí
├── scratch_the_pipe_detector.py       # Phán định vết xước trên thân ống
├── semi_permeable_membrane.py         # Phán định độ phủ màng bán thấm
└── foreign_object_detector.py         # Phán định dị vật bất thường (PatchCore)
```

---

## 3. Nguyên lý phán định điển hình

### 3.1. Đo khoảng cách khe hở (`SlitWeldInspector`)
1. Lấy thông số Master của đoạn thẳng: `widthMin` và `widthMax`.
2. Trích xuất đường biên mép mối ghép từ ảnh camera tại vị trí đường line đã cấu hình (`xStart, yStart, xEnd, yEnd`).
3. Tính toán khoảng cách Euclidean thực tế giữa 2 mép biên.
4. Đánh giá:
   $$\text{Nếu } \text{widthMin} \le \text{Khoảng cách đo} \le \text{widthMax} \implies \mathbf{OK} \quad \text{Ngược lại} \implies \mathbf{NG}$$

### 3.2. Đo độ rộng mối hàn (`MeasurementWeldInspector`)
1. Lấy 5 mức ngưỡng độ rộng (`level1` đến `level5`) từ Master.
2. Cắt lát vuông góc với trục tâm mối hàn tại các vị trí kiểm tra.
3. Đo bề rộng thực tế của lát cắt và so khớp theo từng bậc dung sai.

### 3.3. Kiểm tra bọt khí đường hàn (`AirBubblesItemInspector`)
1. Đối chiếu mặt nạ phân đoạn đường hàn (`weld_polygon`) và trục tâm (`weld_center_points`).
2. Chỉ tìm kiếm bọt khí nằm **bên trong** phạm vi đa giác đường hàn (loại bỏ nhiễu từ nền ngoài).
3. Đếm số lượng bọt khí và tính diện tích/đường kính của từng bóng khí. Nếu vượt ngưỡng diện tích cho phép sẽ kết luận `NG`.

---

## 4. Chuẩn hóa dữ liệu trả về

Mỗi Detector đều xuất ra kết quả có cấu trúc nhất quán:
```json
{
    "status": "OK",
    "details": {
        "inspector_name": "SlitWeldInspector",
        "line_id": "0",
        "measured_val": 1.25,
        "min_limit": 0.1,
        "max_limit": 4.0,
        "unit": "mm"
    },
    "visual_output": {
        "annotated_points": [[1314, 1260], [1148, 1496]],
        "defect_regions": []
    }
}
```
Thông tin này vừa được gửi về giao diện Web vừa được nạp vào log xuất xưởng phục vụ truy xuất nguồn gốc.
