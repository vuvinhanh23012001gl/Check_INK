from app.config import UnetConfig
from app.engines.model_AI import ModelUnet
from app.judger.structure import BorderDetector
import cv2
import numpy as np
from pathlib import Path
obj_unet_config = UnetConfig()
obj_unet_config.path = Path(r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\unet_test_model_vien\unetpp.pth")
obj_unet = ModelUnet(obj_unet_config)
border = BorderDetector(obj_unet)

# ================= BẮT ĐẦU VIẾT TỪ ĐÂY =================

# 1. Đọc ảnh đầu vào cần xử lý (Thay đường dẫn bằng ảnh thực tế của bạn)
# Nếu chưa có ảnh thật, bạn có thể tạo ảnh dummy bằng lệnh: np.zeros((512, 512, 3), dtype=np.uint8)
image_path = r"C:\Users\anhuv\Desktop\train\Unet_vien\6_7_2026_40_img\img\0_copy (13) - Copy.jpg"

image = cv2.imread(image_path)

if image is None:
    print(f"Không thể đọc được ảnh từ đường dẫn: {image_path}")
    print("Vui lòng kiểm tra lại file ảnh đầu vào.")
else:
    H, W = image.shape[:2]

    # 2. Định nghĩa danh sách các đường thẳng cần kiểm tra cắt biên
    # Mỗi đường thẳng là một list/tuple chứa 4 tọa độ pixel: [x1, y1, x2, y2]
    lines_to_check = [
        [50, 200, 450, 200],  # Đường nằm ngang cắt ngang tầm trung ảnh
        [300, 50, 300, 450],  # Đường dọc cắt từ trên xuống dưới
        [10, 20, 100, 150],  # Đường ngắn nằm ở góc (để test trường hợp không cắt)
    ]

    # 3. Gọi hàm xử lý từ thực thể `border` (BorderDetector)
    # Hàm này tự động gọi obj_unet để lấy mask/polygon và xử lý hình học
    results = border.process_lines_from_image(
        image=image,
        lines=lines_to_check,
        Approx_value=0.002,  # Độ mịn xấp xỉ đa giác (epsilon)
        min_area=100,  # Diện tích tối thiểu để loại bỏ nhiễu hạt
    )

    # 4. Trích xuất đa giác gốc từ mô hình để vẽ khung đối chiếu lên ảnh
    polygon = obj_unet.get_polygon(image, Approx_value=0.002, min_area=100)
    display_image = obj_unet.draw_polygon(image, polygon)

    # 5. Duyệt qua kết quả của từng đường thẳng để in log và vẽ minh họa
    print("\n--- KẾT QUẢ KIỂM TRA ĐƯỜNG BIÊN ---")
    for res in results:
        idx = res["line_index"]
        x1, y1, x2, y2 = res["original_line"]

        if res["is_valid"]:
            p1 = res["intersection_point_1"]
            p2 = res["intersection_point_2"]
            dist = res["distance_pixel"]

            print(f"Đường thẳng {idx}: Cắt đa giác tại {p1} và {res['intersection_point_2']}")
            print(f" -> Khoảng cách bên trong vật thể: {dist:.2f} pixels")

            # 🔹 Vẽ đoạn thẳng giao cắt nằm bên trong đa giác (Màu đỏ, nét dày)
            cv2.line(display_image, p1, p2, (0, 0, 255), 3)

            # 🔹 Chấm 2 nút tròn tại vị trí giao điểm (Màu xanh dương)
            cv2.circle(display_image, p1, 5, (255, 0, 0), -1)
            cv2.circle(display_image, p2, 5, (255, 0, 0), -1)

            # 🔹 Viết chữ hiển thị số pixel đo được lên trên đoạn thẳng (Màu vàng)
            text_pos = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2 - 10)
            cv2.putText(
                display_image,
                f"{dist:.1f}px",
                text_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
            )
        else:
            print(f"Đường thẳng {idx}: KHÔNG cắt qua vùng đa giác vật thể.")
            # Vẽ đường không cắt dạng nét mảnh màu xám để nhận biết vị trí của nó
            cv2.line(display_image, (x1, y1), (x2, y2), (128, 128, 128), 1)

    # 6. Hiển thị kết quả trực quan lên màn hình bằng OpenCV
    cv2.imshow("Result Segmentation & Line Tracking", display_image)
    print("\n[INFO] Đang hiển thị ảnh kết quả. Nhấn phím bất kỳ để đóng cửa sổ.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# python -m app.tests.test_judment.test_surface.test_border_detector





# from app.config import UnetConfig
# from app.engines.model_AI import ModelUnet
# from app.judger.structure import BorderDetector
# import cv2
# from pathlib import Path

# # ================= KHỞI TẠO MODEL =================
# obj_unet_config = UnetConfig()
# obj_unet_config.path = Path(
#     r"C:\Disk D\Project\Python_Detect_Width_Line\code\app\unet_test_model_vien\unetpp.pth"
# )

# obj_unet = ModelUnet(obj_unet_config)
# border = BorderDetector(obj_unet)

# # ================= THÔNG SỐ =================

# # None nếu không resize
# resize_size = (1024, 1024)  # (width, height)

# image_path = r"C:\Users\anhuv\Desktop\train\Unet_vien\6_7_2026_40_img\img\0_copy (13) - Copy.jpg"

# # ================= ĐỌC ẢNH =================

# image = cv2.imread(image_path)

# if image is None:
#     print(f"Không thể đọc được ảnh: {image_path}")
#     exit()

# # Lưu kích thước gốc
# original_h, original_w = image.shape[:2]

# # Resize nếu cần
# if resize_size is not None:
#     image = cv2.resize(
#         image,
#         resize_size,
#         interpolation=cv2.INTER_LINEAR
#     )

# H, W = image.shape[:2]

# print(f"Original Size : {original_w} x {original_h}")
# print(f"Resize Size   : {W} x {H}")

# # ================= ĐƯỜNG THẲNG CẦN KIỂM TRA =================

# lines_to_check = [
#     [50, 200, 450, 200],
#     [300, 50, 300, 450],
#     [10, 20, 100, 150],
# ]

# # Scale line nếu resize
# if resize_size is not None:

#     scale_x = W / original_w
#     scale_y = H / original_h

#     scaled_lines = []

#     for x1, y1, x2, y2 in lines_to_check:

#         scaled_lines.append([
#             int(x1 * scale_x),
#             int(y1 * scale_y),
#             int(x2 * scale_x),
#             int(y2 * scale_y),
#         ])

#     lines_to_check = scaled_lines

# # ================= XỬ LÝ =================

# results = border.process_lines_from_image(
#     image=image,
#     lines=lines_to_check,
#     Approx_value=0.002,
#     min_area=100,
# )

# # ================= LẤY POLYGON =================

# polygon = obj_unet.get_polygon(
#     image,
#     Approx_value=0.002,
#     min_area=100
# )

# display_image = obj_unet.draw_polygon(
#     image.copy(),
#     polygon
# )

# # ================= HIỂN THỊ KẾT QUẢ =================

# print("\n========== RESULT ==========\n")

# for res in results:

#     idx = res["line_index"]
#     x1, y1, x2, y2 = res["original_line"]

#     if res["is_valid"]:

#         p1 = tuple(res["intersection_point_1"])
#         p2 = tuple(res["intersection_point_2"])

#         dist = res["distance_pixel"]

#         print(f"Line {idx}")
#         print(f"Intersection 1 : {p1}")
#         print(f"Intersection 2 : {p2}")
#         print(f"Distance       : {dist:.2f} px")
#         print()

#         # Đường nằm trong polygon
#         cv2.line(
#             display_image,
#             p1,
#             p2,
#             (0, 0, 255),
#             3
#         )

#         # Hai điểm giao
#         cv2.circle(
#             display_image,
#             p1,
#             5,
#             (255, 0, 0),
#             -1
#         )

#         cv2.circle(
#             display_image,
#             p2,
#             5,
#             (255, 0, 0),
#             -1
#         )

#         # Hiển thị khoảng cách
#         text_pos = (
#             (p1[0] + p2[0]) // 2,
#             (p1[1] + p2[1]) // 2 - 10,
#         )

#         cv2.putText(
#             display_image,
#             f"{dist:.1f}px",
#             text_pos,
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6,
#             (0, 255, 255),
#             2,
#         )

#     else:

#         print(f"Line {idx}: Không cắt polygon")

#         cv2.line(
#             display_image,
#             (x1, y1),
#             (x2, y2),
#             (128, 128, 128),
#             1,
#         )

# # ================= SHOW =================

# cv2.imshow("Segmentation Result", display_image)

# print("\nNhấn phím bất kỳ để thoát...")

# cv2.waitKey(0)
# cv2.destroyAllWindows()