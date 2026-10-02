# Hệ Thống Tài Liệu Dự Án (Documentation Hub)

Hệ thống tài liệu này được tổ chức theo quy chuẩn tài liệu kỹ thuật tại [`cach_luu_doc.md`](file:///c:/Disk%20D/Project/Python_Detect_Width_Line/code/app/cach_luu_doc.md), phân định rõ ràng giữa **Nghiệp vụ (Features)**, **Kiến trúc mã nguồn (Modules)** và **Quản lý công việc (Tasks)**.

---

## 1. Cấu trúc thư mục

```text
.agents/docs/
├── README.md                      # Chỉ mục và hướng dẫn điều hướng tài liệu
├── features/                      # Phần mềm làm gì? (Nghiệp vụ / Chức năng - Tồn tại lâu dài)
│   ├── overview.md                # Tổng quan mục đích và luồng vận hành sản xuất
│   ├── master_adjustment.md       # Nghiệp vụ điều chỉnh Master & quy ước phán định
│   ├── capture_and_inspection.md  # Nghiệp vụ chụp ảnh tự động và kiểm tra tự động
│   ├── calibration.md             # Nghiệp vụ hiệu chuẩn kích thước (mm <-> pixel)
│   └── product_management.md      # Nghiệp vụ quản lý Model sản phẩm & Điểm chụp
├── modules/                       # Code được tổ chức thế nào? (Kỹ thuật / Kiến trúc - Tồn tại lâu dài)
│   ├── architecture_overview.md   # Kiến trúc hệ thống, Container & Pipeline chạy ngầm
│   ├── ai_engines.md              # Kiến trúc các Engine AI (YOLO, UNet, PatchCore)
│   ├── judger.md                  # Module phán định quy chuẩn (Judger Detectors)
│   ├── hardware_integration.md    # Giao tiếp phần cứng (Serial ARM/IAI & Camera)
│   ├── storage_and_repositories.md# Lưu trữ dữ liệu JSON & tầng Repository
│   └── frontend_architecture.md   # Kiến trúc Canvas & Event Tool phía Frontend
└── tasks/                         # Đang cần làm gì? (Quản lý công việc - Theo vòng đời task)
    ├── task_weld_bubble_detection.md     # Task tích hợp phát hiện bọt khí đường hàn
    ├── task_fix_slit_inspector_undefined.md # Task xử lý lỗi key undefined trong Master Slit
    └── task_roadmap.md            # Lộ trình kỹ thuật, các cải tiến và hạn chế cần xử lý
```

---

## 2. Tiêu chí phân loại tài liệu

| Thư mục | Trả lời câu hỏi | Phạm vi | Thời gian tồn tại | Cập nhật khi nào? |
| :--- | :--- | :--- | :--- | :--- |
| **`features/`** | **Phần mềm làm gì?** | Nghiệp vụ, hành vi giao diện người dùng, quy trình kiểm tra chất lượng trên dây chuyền. | Lâu dài | Khi thay đổi chức năng, luồng vận hành của máy hoặc quy trình kiểm tra. |
| **`modules/`** | **Code tổ chức ra sao?** | Kỹ thuật, kiến trúc class/service, API schema, luồng dữ liệu, giao tiếp phần cứng và AI. | Lâu dài | Khi refactor code, thêm/sửa module, đổi API hoặc thay đổi kiến trúc nội bộ. |
| **`tasks/`** | **Đang cần làm gì?** | Một yêu cầu cụ thể, kế hoạch thực thi chi tiết, bug fix, task nâng cấp tính năng. | Theo vòng đời task | Khi bắt đầu task mới, cập nhật tiến độ hoặc hoàn thành nghiệm thu. |

---

## 3. Hướng dẫn dành cho Developer & AI Agent

1. **Trước khi bắt đầu task mới:**
   - Tra cứu `features/` để hiểu đúng nghiệp vụ bài toán.
   - Đọc `modules/` để nắm rõ cấu trúc module sẽ tác động, tránh phá vỡ giao thức thiết bị hoặc kiến trúc đa luồng.
   - Tạo file kế hoạch trong `tasks/task_<ten_cong_viec>.md`.
2. **Trong quá trình thực thi:**
   - Tuân thủ quy tắc tại `.agents/rules/AGENTS.md` và `.agents/rules/project_standards.md`.
   - Cập nhật tiến độ vào file task tương ứng.
3. **Khi hoàn thành:**
   - Cập nhật các thay đổi kiến trúc vào `modules/` nếu có refactor.
   - Đóng trạng thái trong `tasks/`.
