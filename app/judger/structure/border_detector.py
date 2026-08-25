import cv2
import numpy as np
from app.engines.model_AI import ModelUnet
from .base_ai import BaseJudgerAI

class BorderDetector(BaseJudgerAI):
    """Lớp xử lý kiểm tra các đường thẳng cắt qua đa giác (Polygon) được trích
    xuất từ mô hình ModelUnet.
    """
    def __init__(self, unet_model:ModelUnet):
        """Khởi tạo BorderDetector với một thực thể của ModelUnet.
        Args:
            unet_model (ModelUnet): Thực thể của mô hình Unet đã được load trọng
            số.
        """
        super().__init__()
        self.unet_model = unet_model

    def define(self, image, lines, Approx_value=0.002, min_area=100):
        """Lấy kết quả giao giữa line runtime và polygon từ ảnh."""
        return self.process_lines_from_image(image, lines, Approx_value, min_area)

    def compare(self, standard_data, runtime_data):
        """So sánh dữ liệu đường biên chuẩn với dữ liệu runtime."""
        raise NotImplementedError

    def judge(self, comparison_data):
        """Phán định dữ liệu đường biên thành OK hoặc NG."""
        raise NotImplementedError


    def process_lines_from_image(
        self,
        image: np.ndarray,
        lines: list,
        Approx_value: float = 0.002,
        min_area: int = 100,
    ) -> list[dict]:
        """Nhận vào ảnh gốc, tự động chạy qua ModelUnet để lấy polygon, sau đó
        tìm giao điểm với danh sách đường thẳng và tính khoảng cách pixel.
        Args:
            image (np.ndarray): Ảnh gốc đầu vào (BGR).
            lines (list): Danh sách các đường thẳng, mỗi phần tử dạng (x1, y1,
            x2, y2).
            Approx_value (float): Hệ số xấp xỉ khoảng cách cho hàm
            cv2.approxPolyDP.
            min_area (int): Diện tích tối thiểu để lọc contour của đa giác.
        Returns:
            list[dict]: Danh sách chứa thông tin tọa độ giao điểm và khoảng cách
            từng đường thẳng.
        """
        results = []
        H, W = image.shape[:2]

        # 1. Gọi hàm trích xuất Polygon trực tiếp từ thực thể ModelUnet truyền vào
        polygon = self.unet_model.get_polygon(
            image, Approx_value=Approx_value, min_area=min_area
        )
        if polygon is None or len(polygon) < 3:
            print(
                "Warning: Không tìm thấy đa giác hợp lệ (hoặc ít hơn 3 đỉnh) từ ảnh."
            )
            return results
        # 2. Tạo một mặt nạ chứa vùng đa giác (tô kín đa giác bằng màu trắng 255)
        poly_mask = np.zeros((H, W), dtype=np.uint8)
        cv2.drawContours(poly_mask, [polygon], -1, 255, thickness=-1)
        # 3. Duyệt qua từng đường thẳng trong danh sách
        for idx, line in enumerate(lines):
            x1, y1, x2, y2 = line
            # Kéo dài đường thẳng ra rìa ảnh để chắc chắn cắt qua toàn bộ Polygon nếu nó đi qua
            extended_line = self._extend_line(x1, y1, x2, y2, W, H)
            if extended_line is None:
                continue
            ex1, ey1, ex2, ey2 = extended_line
            # Tạo mặt nạ nhị phân riêng cho đường thẳng này (độ dày 1 pixel)
            line_mask = np.zeros((H, W), dtype=np.uint8)
            cv2.line(line_mask, (ex1, ey1), (ex2, ey2), 255, thickness=1)
            # Phép toán Bitwise AND để lấy phần giao tuyến nằm TRONG đa giác
            intersection_mask = cv2.bitwise_and(line_mask, poly_mask)
            # Tìm tọa độ các pixel có giá trị màu trắng (255)
            pts = np.argwhere(intersection_mask == 255)
            # Đường thẳng cắt đa giác tại ít nhất 2 điểm biên (đầu và cuối phân đoạn)
            if len(pts) >= 2:
                # np.argwhere trả về dạng (hàng, cột) ứng với (y, x) -> Cần đảo ngược lại thành (x, y)
                p1 = (pts[0][1], pts[0][0])
                p2 = (pts[-1][1], pts[-1][0])
                # Tính khoảng cách Euclidean giữa 2 điểm (pixel)
                distance_pixel = np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
                results.append(
                    {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": p1,
                        "intersection_point_2": p2,
                        "distance_pixel": float(distance_pixel),
                        "is_valid": True,
                    }
                )
            else:
                # Đường thẳng nằm ngoài hoặc chỉ tiếp xúc rìa (1 điểm), không tính là cắt qua
                results.append(
                    {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": None,
                        "intersection_point_2": None,
                        "distance_pixel": 0.0,
                        "is_valid": False,
                    }
                )
        return results


    def _extend_line(self, x1, y1, x2, y2, W, H):
        """Hàm bổ trợ: Kéo dài đoạn thẳng hữu hạn ra tận biên ảnh (vô hạn) để
        phục vụ cắt đa giác chính xác.
        """
        if x1 == x2 and y1 == y2:
            return None
        # Đường thẳng đứng (Song song trục Oy)
        if x1 == x2:
            return (x1, 0, x1, H - 1)
        # Tính toán phương trình y = ax + b
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        # Tìm 2 giao điểm tại 2 biên trái/phải của ảnh (x = 0 và x = W - 1)
        ly1 = int(b)
        ly2 = int(a * (W - 1) + b)
        return (0, ly1, W - 1, ly2)