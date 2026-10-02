# Task: Sửa lỗi Sinh key "undefined" trong SlitWeldInspector (Bug Fix)

## 1. Thông tin Nhiệm vụ
- **Mã công việc**: `BUG-SLIT-01`
- **Tình trạng**: Hoàn thành (Completed)
- **Mức độ ưu tiên**: Nghiêm trọng (Critical)
- **Ngày hoàn thành**: 2026-10-02

---

## 2. Mô tả Hiện tượng & Nguyên nhân Gốc rễ (Root Cause Analysis)

### 2.1. Hiện tượng lỗi
Trong công cụ cấu hình Master Adjustment (`/law_regulation`), khi người dùng click vào một đường thẳng khe hàn (`SlitWeldInspector`) đã vẽ trên Canvas để chỉnh sửa lại thông số (ví dụ sửa `widthMax` từ `4` thành `7`), hệ thống không cập nhật vào key `"0"` hiện có mà lại sinh thêm một key `"undefined"` song song:

```json
"SlitWeldInspector": {
    "0": {
        "nameLine": "1",
        "widthMin": 0.1,
        "widthMax": 4,
        "xStart": 1314, "yStart": 1260, "xEnd": 1148, "yEnd": 1496,
        "coordinateSpace": "image"
    },
    "undefined": {
        "nameLine": "1",
        "widthMin": 0.1,
        "widthMax": 7,
        "xStart": 1314, "yStart": 1260, "xEnd": 1148, "yEnd": 1496,
        "coordinateSpace": "image"
    }
}
```

### 2.2. Phân tích Nguyên nhân Gốc rễ
1. **Frontend mismatch property name**:
   - Model lưu trữ đối tượng đường kẻ ([`model_slit.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/model/model_slit.js)) sử dụng thuộc tính là `this.id_line`.
   - Tuy nhiên, trong [`slit_tool.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/tool/slit_tool.js), hàm `func_callback_click_on_line_drawn` lại đọc `measurementClone.lineId`. Vì thuộc tính này không tồn tại, giá trị nhận được là `undefined`.
2. **Frontend Type Coercion & Key Collisions**:
   - Trong [`slit_item_inspector.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/services/slit_item_inspector.js), hàm `addSlit` so sánh `item.id_line === modelSlit.id_line` (so sánh nghiêm ngặt giữa kiểu `number` và `string`), dẫn đến không tìm thấy bản ghi cũ để ghi đè.
   - Khi tệp `config_judgment_law.json` đã từng bị lưu vết `"undefined"`, hàm `findLineByCoordinate` duyệt mảng ngược từ dưới lên sẽ bắt trúng object `"undefined"` thay vì object `"0"`.
3. **Backend thiếu phòng vệ**:
   - Backend [`JudmentLawProductRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/judment_law_product_reponsitory.py) trước đó lưu thẳng toàn bộ JSON nhận được từ client mà không kiểm tra tính hợp lệ của các key.

---

## 3. Giải pháp Kỹ thuật Đã Triển khai (Code-Level Resolution)

> **Nguyên tắc**: Sửa triệt để bằng mã nguồn ở cả Frontend và Backend, không sửa thủ công tệp JSON. Giá trị mới từ `undefined` tự động ghi đè lên item `0` và loại bỏ hoàn toàn key `undefined`.

### 3.1. Sửa đổi Frontend (`slit_tool.js` & `slit_item_inspector.js`)
- **[`slit_tool.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/tool/slit_tool.js)**:
  - Thay thế toàn bộ `measurementClone.lineId` thành `measurementClone.id_line`.
  - Bổ sung fallback an toàn: `const currentLineId = measurementClone.id_line ?? "0"`.
- **[`slit_item_inspector.js`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/static/js/services/slit_item_inspector.js)**:
  - Trong `fromDict(data)`: Tự động phát hiện nếu tồn tại key `"undefined"`, hợp nhất dữ liệu vào key `"0"` và xóa bỏ `"undefined"` ngay khi load vào bộ nhớ client:
    ```javascript
    if ("undefined" in data) {
        if (!data["0"]) data["0"] = {};
        Object.assign(data["0"], data["undefined"]);
        delete data["undefined"];
    }
    ```
  - Trong `addSlit(modelSlit)`: Ép kiểu chuỗi khi so sánh: `String(item.id_line) === String(modelSlit.id_line)`.
  - Trong `toDict()`: Kiểm tra nếu `id_line` là `"undefined"` hoặc `null`, ép về `"0"`.

### 3.2. Sửa đổi Backend (`judment_law_product_reponsitory.py` & `api_tool_law_regulations.py`)
- **[`JudmentLawProductRepository`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/repository/judment_law_product_reponsitory.py)**:
  - Bổ sung phương thức tĩnh đệ quy:
    ```python
    @staticmethod
    def clean_undefined_keys(data: dict) -> bool:
        changed = False
        if not isinstance(data, dict):
            return False
        for k, v in list(data.items()):
            if isinstance(v, dict):
                if "undefined" in v:
                    undefined_val = v.pop("undefined")
                    if "0" in v and isinstance(v["0"], dict) and isinstance(undefined_val, dict):
                        v["0"].update(undefined_val)
                    else:
                        v["0"] = undefined_val
                    changed = True
                if JudmentLawProductRepository.clean_undefined_keys(v):
                    changed = True
        return changed
    ```
  - Tự động gọi `clean_undefined_keys` trong `_load()`, `save()`, và `update_data()`.
- **[`api_tool_law_regulations.py`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/app/routers/api_tool_law_regulations.py)**:
  - Gọi làm sạch dữ liệu trong cả 2 API GET `/law_regulation/` và POST `/law_regulation/save`.

---

## 4. Kết quả & Xác minh
- Dữ liệu `config_judgment_law.json` tự động được dọn sạch key `"undefined"` ngay khi API hoặc Repository khởi động.
- Mọi thao tác vẽ mới, sửa đường cũ, xóa đường trên Web Canvas diễn ra mượt mà, định danh đường (`0`, `1`, `2`) được bảo toàn chính xác.
