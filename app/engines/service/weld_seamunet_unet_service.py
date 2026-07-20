from app.engines.model_AI import ModelUnet
import numpy as np
import cv2
from skimage.morphology import skeletonize
from scipy.spatial.distance import cdist
from scipy.spatial import cKDTree
from app.config import UnetCofigAutoDetectLineMaster
import time
from collections import defaultdict

class WeldMeamunetUnetService:
    def __init__(self, autoDetectLineMaster: UnetCofigAutoDetectLineMaster, infeUnet: ModelUnet):
        """Khởi tạo service cấu hình và mô hình UNet để tự động phát hiện đường line.

        Args:
            autoDetectLineMaster (UnetCofigAutoDetectLineMaster): Đối tượng chứa cấu hình phát hiện đường line master.
            infeUnet (ModelUnet): Instance của mô hình UNet phục vụ việc dự đoán mặt nạ phân đoạn (segmentation mask).
        """
        self.infeUnet = infeUnet
        self.auto_detect_line_master = autoDetectLineMaster

    def get_mask_and_polygon(self, img):
        """Dự đoán mask phân đoạn từ ảnh đầu vào và trích xuất ra danh sách các đa giác (polygons) biên.

        Args:
            img (np.ndarray): Ảnh gốc đầu vào (BGR hoặc Grayscale).

        Returns:
            tuple: Gồm 2 phần tử:
                - mask (np.ndarray): Mặt nạ nhị phân kết quả từ mô hình UNet.
                - polygons (list[np.ndarray]): Danh sách các tọa độ đỉnh đa giác đại diện cho biên vật thể.
        """
        mask = self.infeUnet.get_mask(img)
        polygons = self.find_polygons(mask, self.infeUnet.config.epsilon_ratio, self.infeUnet.config.min_area)
        return mask, polygons

    def get_mask(self, img):
        """Lấy mặt nạ nhị phân (mask) từ mô hình UNet cho ảnh đầu vào.

        Args:
            img (np.ndarray): Ảnh gốc đầu vào cần phân đoạn.

        Returns:
            np.ndarray: Mặt nạ nhị phân dự đoán từ mô hình UNet.
        """
        mask = self.infeUnet.get_mask(img)
        return mask

    def automate_sampling_for_checking(self, img, edge_point_spacing_polygons=-1, length_line_extend=-1):
        """Tự động thực hiện quy trình lấy mẫu biên, trích xuất skeleton và sinh các đường đo chiều rộng vật thể.

        Args:
            img (np.ndarray): Ảnh gốc đầu vào phục vụ kiểm tra.
            edge_point_spacing_polygons (int, optional): Khoảng cách lấy mẫu điểm trên biên đa giác. Nếu bằng -1 sẽ dùng giá trị trong cấu hình mặc định. Defaults to -1.
            length_line_extend (int, optional): Độ dài kéo dài thêm ở mỗi đầu của đường line kết quả. Nếu bằng -1 sẽ dùng cấu hình mặc định. Defaults to -1.

        Returns:
            tuple: Gồm 3 phần tử:
                - lines_final (list[dict]): Danh sách các đoạn thẳng đo chiều rộng hoàn chỉnh sau khi đã lọc và kéo dài.
                - (width, height) (tuple): Kích thước (rộng, cao) của ảnh đầu vào.
                - polygon (list[np.ndarray]): Danh sách đa giác biên của vật thể được phát hiện.
        """
        total_start = time.perf_counter()
        height, width = img.shape[:2]
        t = time.perf_counter()
        mask, polygon = self.get_mask_and_polygon(img)
        print(f"1. get_mask_and_polygon      : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        skeleton = self.get_skeleton(mask)
        print(f"2. get_skeleton             : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        center_points = self.get_main_skeleton_points(skeleton)
        print(f"3. get_main_skeleton_points : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        center_points = self.sample_skeleton_points(
            center_points,
            spacing=self.auto_detect_line_master.distance_between_points_center_point
        )
        print(f"4. sample_skeleton_points   : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        spacing = (
            edge_point_spacing_polygons
            if edge_point_spacing_polygons != -1
            else self.auto_detect_line_master.edge_point_spacing_polygons
        )
        polygon_points = self.get_polygon_points(polygon, spacing=spacing)
        print(f"5. get_polygon_points       : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        lines = self.extract_width_lines(
            polygon,
            polygon_points,
            center_points,
            search_length=self.auto_detect_line_master.intersection_detection_range,
            min_length=self.auto_detect_line_master.minimum_allowable_width,
            max_length=self.auto_detect_line_master.maximum_width_allowed
        )
        print(f"6. extract_width_lines      : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        take_lines = self.filter_close_lines(
            lines,
            min_spacing=self.auto_detect_line_master.minimum_length_to_remove_line
        )
        print(f"7. filter_close_lines       : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        length_line = (
            length_line_extend
            if length_line_extend != -1
            else self.auto_detect_line_master.length_extended_at_each_end
        )
        lines_final = self.extend_lines(take_lines, extend_length=length_line)
        print(f"8. extend_lines             : {time.perf_counter() - t:.3f} s")
        print(f"\n===== TOTAL: {time.perf_counter() - total_start:.3f} s =====")
        return lines_final, (width, height), polygon

    def draw_lines(self, image, lines, color=(255, 255, 0), thickness=1):
        """Vẽ danh sách các đoạn thẳng đo đạc (đã hoặc chưa kéo dài) lên bề mặt ảnh.

        Args:
            image (np.ndarray): Ảnh nền cần vẽ các đoạn thẳng lên (thay đổi trực tiếp trên ảnh).
            lines (list[dict]): Danh sách đoạn thẳng, mỗi phần tử dạng {"p1": (x1, y1), "p2": (x2, y2)}.
            color (tuple, optional): Màu sắc đoạn thẳng dạng BGR. Defaults to (255, 255, 0).
            thickness (int, optional): Độ dày nét vẽ tính bằng pixel. Defaults to 1.

        Returns:
            np.ndarray: Ảnh gốc sau khi đã được vẽ thêm các đoạn thẳng.
        """
        for line in lines:
            cv2.line(image, line["p1"], line["p2"], color, thickness)
        return image

    def draw_polygon_points(self, image, polygon_points, radius=2, color=(0, 0, 255), thickness=-1):
        """Vẽ các điểm lấy mẫu từ biên đa giác (polygon) lên bề mặt ảnh dưới dạng hình tròn nhỏ.

        Args:
            image (np.ndarray): Ảnh nền cần vẽ các điểm lên.
            polygon_points (list[dict]): Danh sách điểm lấy mẫu biên, chứa key "point": [x, y].
            radius (int, optional): Bán kính của điểm tròn vẽ ra. Defaults to 2.
            color (tuple, optional): Màu sắc của điểm dạng BGR. Defaults to (0, 0, 255).
            thickness (int, optional): Độ dày nét vẽ, giá trị -1 tương đương tô kín hình tròn. Defaults to -1.

        Returns:
            np.ndarray: Ảnh sau khi đã vẽ các điểm lấy mẫu biên.
        """
        for item in polygon_points:
            p = item["point"]
            x = int(round(p[0]))
            y = int(round(p[1]))
            cv2.circle(image, (x, y), radius, color, thickness)
        return image

    def extend_lines(self, lines, extend_length=10):
        """Kéo dài tuyến tính các đoạn thẳng hiện tại về cả hai đầu dựa theo hướng vector của chúng.

        Args:
            lines (list[dict]): Danh sách các đoạn thẳng ban đầu gồm "p1" và "p2".
            extend_length (int, optional): Chiều dài (pixel) cần kéo dài thêm ở mỗi đầu đoạn thẳng. Defaults to 10.

        Returns:
            list[dict]: Danh sách đoạn thẳng mới sau khi kéo dài, kèm theo thuộc tính "length" được cập nhật.
        """
        extended_lines = []
        for line in lines:
            p1 = np.array(line["p1"], dtype=np.float32)
            p2 = np.array(line["p2"], dtype=np.float32)
            direction = p2 - p1
            length = np.linalg.norm(direction)
            if length < 1:
                continue
            direction /= length
            new_p1 = p1 - direction * extend_length
            new_p2 = p2 + direction * extend_length
            extended_lines.append({
                "p1": (int(round(new_p1[0])), int(round(new_p1[1]))),
                "p2": (int(round(new_p2[0])), int(round(new_p2[1]))),
                "length": float(np.linalg.norm(new_p2 - new_p1))
            })
        return extended_lines

    def line_segment_intersection(self, p1, p2, q1, q2):
        """Tìm giao điểm giữa hai đoạn thẳng p1p2 và q1q2 bằng giải thuật nhân chéo vector.

        Args:
            p1 (np.ndarray): Tọa độ điểm đầu đoạn thẳng thứ nhất [x, y].
            p2 (np.ndarray): Tọa độ điểm cuối đoạn thẳng thứ nhất [x, y].
            q1 (np.ndarray): Tọa độ điểm đầu đoạn thẳng thứ hai [x, y].
            q2 (np.ndarray): Tọa độ điểm cuối đoạn thẳng thứ hai [x, y].

        Returns:
            np.ndarray | None: Tọa độ giao điểm [x, y] nếu hai đoạn cắt nhau, ngược lại trả về None.
        """
        r = p2 - p1
        s = q2 - q1
        denom = r[0] * s[1] - r[1] * s[0]
        if abs(denom) < 1e-8:
            return None
        qp = q1 - p1
        t = (qp[0] * s[1] - qp[1] * s[0]) / denom
        u = (qp[0] * r[1] - qp[1] * r[0]) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p1 + t * r
        return None

    def extract_width_lines(self, polygons, polygon_points, center_points, search_length=1000, min_length=5, max_length=100):
        """Sinh các đoạn thẳng đo chiều rộng bằng cách bắn tia pháp tuyến từ biên hướng về phía tâm skeleton và tìm giao điểm đối diện.

        Args:
            polygons (list[np.ndarray]): Danh sách các đa giác biên bao quanh cấu trúc vật thể.
            polygon_points (list[dict]): Danh sách các điểm đã được lấy mẫu phân bổ trên biên đa giác.
            center_points (np.ndarray): Tập hợp chuỗi điểm xương sống (skeleton center points).
            search_length (int, optional): Khoảng cách tối đa (pixel) mà tia pháp tuyến tìm kiếm giao điểm có thể bắn tới. Defaults to 1000.
            min_length (int, optional): Chiều rộng tối thiểu cho phép chấp nhận đoạn thẳng đo đạc. Defaults to 5.
            max_length (int, optional): Chiều rộng tối đa cho phép chấp nhận đoạn thẳng đo đạc. Defaults to 100.

        Returns:
            list[dict]: Danh sách chứa thông tin các đường line đo chiều rộng thỏa mãn điều kiện lọc kích thước.
        """
        lines = []
        if len(center_points) == 0:
            return lines
        tree = cKDTree(center_points)
        for item in polygon_points:
            p = item["point"].astype(np.float32)
            poly_idx = item["poly_idx"]
            edge_idx = item["edge_idx"]
            poly = polygons[poly_idx]
            pts = poly.reshape(-1, 2).astype(np.float32)
            a = pts[edge_idx]
            b = pts[(edge_idx + 1) % len(pts)]
            _, idx = tree.query(p)
            center = center_points[idx].astype(np.float32)
            edge = b - a
            edge_len = np.linalg.norm(edge)
            if edge_len < 1:
                continue
            tangent = edge / edge_len
            normal = np.array([-tangent[1], tangent[0]], dtype=np.float32)
            if np.dot(normal, center - p) < 0:
                normal *= -1
            ray_end = p + normal * search_length
            intersections = []
            for poly2 in polygons:
                pts2 = poly2.reshape(-1, 2).astype(np.float32)
                n2 = len(pts2)
                for i in range(n2):
                    s1 = pts2[i]
                    s2 = pts2[(i + 1) % n2]
                    inter = self.line_segment_intersection(p, ray_end, s1, s2)
                    if inter is None:
                        continue
                    dist = np.linalg.norm(inter - p)
                    if dist > 1:
                        intersections.append((dist, inter))
            if len(intersections) == 0:
                continue
            intersections.sort(key=lambda x: x[0])
            length = intersections[0][0]
            p2 = intersections[0][1]
            if length < min_length or length > max_length:
                continue
            lines.append({
                "p1": (int(round(p[0])), int(round(p[1]))),
                "p2": (int(round(p2[0])), int(round(p2[1]))),
                "length": float(length)
            })
        return lines

    def get_polygon_points(self, polygons, spacing=10):
        """Lấy mẫu các điểm phân bố cách đều nhau theo một khoảng nhất định dọc trên các cạnh của đa giác biên.

        Args:
            polygons (list[np.ndarray]): Danh sách cấu trúc đa giác thu được từ contour của mask.
            spacing (int, optional): Khoảng cách pixel tối thiểu giữa hai điểm lấy mẫu liên tiếp trên biên. Defaults to 10.

        Returns:
            list[dict]: Danh sách thông tin điểm lấy mẫu biên kèm chỉ số đa giác (`poly_idx`) và chỉ số cạnh (`edge_idx`).
        """
        polygon_points = []
        for poly_idx, poly in enumerate(polygons):
            pts = poly.reshape(-1, 2).astype(np.float32)
            if len(pts) < 2:
                continue
            pts = np.vstack([pts, pts[0]])
            remain = 0.0
            for edge_idx in range(len(pts) - 1):
                p1 = pts[edge_idx]
                p2 = pts[edge_idx + 1]
                edge = p2 - p1
                edge_len = np.linalg.norm(edge)
                if edge_len < 1e-6:
                    continue
                direction = edge / edge_len
                d = remain
                while d <= edge_len:
                    point = p1 + direction * d
                    polygon_points.append({
                        "point": point.copy(),
                        "poly_idx": poly_idx,
                        "edge_idx": edge_idx
                    })
                    d += spacing
                remain = d - edge_len
        return polygon_points

    def draw_points(self, img, points, radius=2, color=(0, 0, 255), thickness=-1):
        """Vẽ danh sách các điểm bất kỳ (ví dụ: điểm trung tâm skeleton) lên bề mặt ảnh.

        Args:
            img (np.ndarray): Ảnh nền đích cần vẽ điểm lên.
            points (Iterable): Tập hợp hoặc mảng chứa các cặp tọa độ điểm (x, y).
            radius (int, optional): Bán kính vòng tròn cho mỗi điểm. Defaults to 2.
            color (tuple, optional): Màu sắc của điểm dạng BGR. Defaults to (0, 0, 255).
            thickness (int, optional): Độ dày nét vẽ, -1 để đổ màu đặc hoàn toàn. Defaults to -1.

        Returns:
            np.ndarray: Ảnh đích sau khi được vẽ thêm chuỗi các điểm chỉ định.
        """
        for x, y in points:
            cv2.circle(img, (int(x), int(y)), radius, color, thickness)
        return img

    def sample_skeleton_points(self, points, spacing=10):
        """Lấy mẫu lại chuỗi điểm skeleton đã sắp xếp sao cho khoảng cách tích lũy giữa các điểm lấy mẫu bằng giá trị spacing.

        Args:
            points (np.ndarray): Mảng danh sách các điểm skeleton ban đầu đã sắp xếp thứ tự dọc trục.
            spacing (int, optional): Khoảng cách tích lũy tối thiểu để giữ lại điểm lấy mẫu tiếp theo. Defaults to 10.

        Returns:
            np.ndarray: Mảng chứa tập hợp các điểm skeleton sau khi trích xuất lấy mẫu.
        """
        if len(points) < 2:
            return points
        sampled = [points[0]]
        accumulated = 0
        for i in range(1, len(points)):
            d = np.linalg.norm(points[i] - points[i - 1])
            accumulated += d
            if accumulated >= spacing:
                sampled.append(points[i])
                accumulated = 0
        return np.array(sampled)

    def get_main_skeleton_points(self, skeleton):
        """Trích xuất và sắp xếp tuần tự các pixel thuộc đường trục skeleton từ điểm bắt đầu xa nhất (dùng thuật toán Greedy/Nearest Neighbor).

        Args:
            skeleton (np.ndarray): Ảnh ma trận nhị phân chứa đường trục xương sống (skeleton).

        Returns:
            np.ndarray: Mảng numpy kích thước (N, 2) lưu chuỗi tọa độ các điểm trục xương sống đã sắp xếp tuần tự.
        """
        ys, xs = np.where(skeleton > 0)
        points = np.column_stack((xs, ys)).astype(np.float32)
        n = len(points)
        if n < 2:
            return points
        D = cdist(points, points)
        start_idx = np.unravel_index(np.argmax(D), D.shape)[0]
        visited = np.zeros(n, dtype=bool)
        ordered = np.empty((n, 2), dtype=np.float32)
        current = start_idx
        for i in range(n):
            ordered[i] = points[current]
            visited[current] = True
            diff = points - points[current]
            dist2 = diff[:, 0] * diff[:, 0] + diff[:, 1] * diff[:, 1]
            dist2[visited] = np.inf
            if i != n - 1:
                current = np.argmin(dist2)
        return ordered

    def get_skeleton(self, mask):
        """Mỏng hóa mặt nạ nhị phân (mask) để trích xuất cấu trúc đường xương sống một pixel (skeletonization).

        Args:
            mask (np.ndarray): Mặt nạ phân đoạn nhị phân chứa đối tượng cần trích xuất trục.

        Returns:
            np.ndarray: Ảnh nhị phân (kiểu dữ liệu uint8) chứa đường skeleton mảnh.
        """
        skeleton = skeletonize(mask > 0)
        return skeleton.astype(np.uint8)

    def get_skeleton_points(self, skeleton):
        """Lấy toàn bộ các cặp tọa độ [x, y] của các pixel có giá trị lớn hơn 0 trên ảnh skeleton.

        Args:
            skeleton (np.ndarray): Ảnh nhị phân skeleton.

        Returns:
            np.ndarray: Mảng lưu trữ tất cả tọa độ pixel thuộc skeleton không theo thứ tự tuyến tính dọc trục.
        """
        ys, xs = np.where(skeleton > 0)
        points = np.column_stack((xs, ys))
        return points

    def clean_mask_opening(self, mask, kernel_size=3, iterations=1):
        """Thực hiện toán tử hình thái học Opening (Bào mòn rồi Giãn nở) giúp lọc sạch đốm nhiễu nhỏ hoặc phần lồi lõm li ti trên mask.

        Args:
            mask (np.ndarray): Mặt nạ phân đoạn nhị phân gốc chứa nhiễu.
            kernel_size (int, optional): Kích thước của kernel cấu trúc vuông (ví dụ: 3 tức kernel kích cỡ 3x3). Defaults to 3.
            iterations (int, optional): Số lần lặp lại tuần tự của phép toán toán tử hình thái học. Defaults to 1.

        Returns:
            np.ndarray: Ảnh mặt nạ nhị phân mới sau khi đã được loại bỏ nhiễu biên và hạt nhỏ.
        """
        mask = mask.astype(np.uint8)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations)
        return mask_clean

    def draw_mask(self, mask, window_name="Mask"):
        """Hiển thị ảnh mặt nạ nhị phân lên màn hình qua OpenCV GUI và tạm dừng luồng cho tới khi nhấn phím ngắt.

        Args:
            mask (np.ndarray): Mặt nạ nhị phân cần hiển thị.
            window_name (str, optional): Tên tiêu đề thanh trạng thái hiển thị của cửa sổ OpenCV window. Defaults to "Mask".
        """
        mask = mask.astype(np.uint8)
        cv2.imshow(window_name, mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_img(self, image, window_name="Image"):
        """Hiển thị ảnh màu hoặc ảnh xám bất kỳ lên màn hình và đợi người dùng bấm nút tắt cửa sổ.

        Args:
            image (np.ndarray): Ma trận mảng dữ liệu ảnh OpenCV cần render xem trực quan.
            window_name (str, optional): Tên tiêu đề của khung window hiển thị ảnh. Defaults to "Image".
        """
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def find_polygons(self, mask, epsilon_ratio=0.002, min_area=100):
        """Tìm kiếm hệ thống các contours trên mask nhị phân và xấp xỉ hóa chúng thành đa giác bằng thuật toán Douglas-Peucker.

        Args:
            mask (np.ndarray): Ảnh nhị phân đầu vào chứa các khối đối tượng.
            epsilon_ratio (float, optional): Tỷ lệ nhân chiều dài chu vi dùng làm ngưỡng khoảng cách xấp xỉ đa giác (epsilon). Defaults to 0.002.
            min_area (int, optional): Diện tích vùng contour tối thiểu để giữ lại, lọc bỏ các đốm nhiễu kích cỡ nhỏ. Defaults to 100.

        Returns:
            list[np.ndarray]: Danh sách các mảng numpy lưu tọa độ các đỉnh của các đa giác biên được chấp nhận.
        """
        mask = mask.astype(np.uint8)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        polygons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            epsilon = epsilon_ratio * cv2.arcLength(cnt, True)
            poly = cv2.approxPolyDP(cnt, epsilon, True)
            polygons.append(poly)
        return polygons

    def draw_polygons(self, image, polygons, color=(0, 255, 0), thickness=2):
        """Vẽ tập hợp các chuỗi đường đa giác (polygons) khép kín lên trên ảnh nền chỉ định.

        Args:
            image (np.ndarray): Ảnh đích chịu tác động vẽ nét biên đa giác trực tiếp.
            polygons (list[np.ndarray]): Danh sách các mảng chứa tập hợp tọa độ các đỉnh đa giác.
            color (tuple, optional): Màu sắc thể hiện đường biên dạng BGR. Defaults to (0, 255, 0).
            thickness (int, optional): Độ dày của nét vẽ bao quanh viền đa giác. Defaults to 2.

        Returns:
            np.ndarray: Ảnh kết quả đã bao gồm các đường nét biên đa giác vừa vẽ.
        """
        for poly in polygons:
            cv2.polylines(image, [poly], True, color, thickness)
        return image

    def filter_close_lines(self, lines, min_spacing=20):
        """Lọc và loại bỏ các đoạn thẳng quá gần nhau bằng cấu trúc Grid-mapping phi tuyến tính nhằm giảm thiểu số lượng đường dư thừa.

        Args:
            lines (list[dict]): Danh sách các đối tượng đoạn thẳng đo đạc cần lọc khoảng cách.
            min_spacing (int, optional): Khoảng cách không gian tối thiểu bắt buộc giữa hai đoạn thẳng bất kỳ để được giữ lại. Defaults to 20.

        Returns:
            list[dict]: Danh sách mới chứa tập hợp các đoạn thẳng thỏa mãn khoảng cách phân tán an toàn.
        """
        if len(lines) <= 1:
            return lines
        cell_size = float(min_spacing)
        grid = defaultdict(list)
        kept = []
        def point_segment_distance(p, a, b):
            ab = b - a
            ab_len2 = np.dot(ab, ab)
            if ab_len2 < 1e-8:
                return np.linalg.norm(p - a)
            t = np.dot(p - a, ab) / ab_len2
            t = np.clip(t, 0.0, 1.0)
            proj = a + t * ab
            return np.linalg.norm(p - proj)
        def segments_intersect(a1, a2, b1, b2):
            def cross(u, v):
                return u[0] * v[1] - u[1] * v[0]
            r = a2 - a1
            s = b2 - b1
            denom = cross(r, s)
            if abs(denom) < 1e-8:
                return False
            qp = b1 - a1
            t = cross(qp, s) / denom
            u = cross(qp, r) / denom
            return (0 <= t <= 1) and (0 <= u <= 1)
        def line_distance(l1, l2):
            a1 = np.asarray(l1["p1"], np.float32)
            a2 = np.asarray(l1["p2"], np.float32)
            b1 = np.asarray(l2["p1"], np.float32)
            b2 = np.asarray(l2["p2"], np.float32)
            if segments_intersect(a1, a2, b1, b2):
                return 0.0
            return min(
                point_segment_distance(a1, b1, b2),
                point_segment_distance(a2, b1, b2),
                point_segment_distance(b1, a1, a2),
                point_segment_distance(b2, a1, a2),
            )
        for line in lines:
            p1 = np.asarray(line["p1"], np.float32)
            p2 = np.asarray(line["p2"], np.float32)
            xmin = min(p1[0], p2[0])
            xmax = max(p1[0], p2[0])
            ymin = min(p1[1], p2[1])
            ymax = max(p1[1], p2[1])
            gx0 = int(xmin // cell_size)
            gx1 = int(xmax // cell_size)
            gy0 = int(ymin // cell_size)
            gy1 = int(ymax // cell_size)
            keep = True
            checked = set()
            for gx in range(gx0, gx1 + 1):
                for gy in range(gy0, gy1 + 1):
                    for other in grid[(gx, gy)]:
                        oid = id(other)
                        if oid in checked:
                            continue
                        checked.add(oid)
                        if line_distance(line, other) < min_spacing:
                            keep = False
                            break
                    if not keep:
                        break
                if not keep:
                    break
            if keep:
                kept.append(line)
                for gx in range(gx0, gx1 + 1):
                    for gy in range(gy0, gy1 + 1):
                        grid[(gx, gy)].append(line)
        return kept

    def get_line_intersection_width(self, img, start_x, start_y, end_x, end_y):
        """Tính toán khoảng cách thực tế (pixel) giữa 2 điểm giao cắt sinh ra khi đường nối (start_x, start_y) và (end_x, end_y) cắt qua biên đa giác.

        Args:
            img (np.ndarray): Ảnh gốc dùng để vẽ kiểm tra debug giao điểm biên.
            start_x (int): Tọa độ trục X điểm bắt đầu của đoạn thẳng định hướng.
            start_y (int): Tọa độ trục Y điểm bắt đầu của đoạn thẳng định hướng.
            end_x (int): Tọa độ trục X điểm kết thúc của đoạn thẳng định hướng.
            end_y (int): Tọa độ trục Y điểm kết thúc của đoạn thẳng định hướng.

        Returns:
            tuple: Gồm 2 phần tử:
                - success (bool): True nếu đường thẳng cắt biên đa giác tại chính xác 2 điểm phân biệt, ngược lại là False.
                - pixel_length (float): Khoảng cách Euclid (chiều rộng) giữa 2 giao điểm, nếu không hợp lệ trả về 0.
        """
        mask = self.infeUnet.get_mask(img)
        cv2.circle(img, (start_x, start_y), 4, (0, 255, 255), -1)
        cv2.circle(img, (end_x, end_y), 4, (0, 255, 255), -1)
        polygons = self.find_polygons(mask, self.infeUnet.config.epsilon_ratio, self.infeUnet.config.min_area)
        p1 = np.array([start_x, start_y], dtype=np.float32)
        p2 = np.array([end_x, end_y], dtype=np.float32)
        intersections = []
        for poly in polygons:
            pts = poly.reshape(-1, 2).astype(np.float32)
            n_pts = len(pts)
            if n_pts < 3:
                continue
            for i in range(n_pts):
                q1 = pts[i]
                q2 = pts[(i + 1) % n_pts]
                inter = self.line_segment_intersection(p1, p2, q1, q2)
                if inter is None:
                    continue
                is_duplicate = False
                for old in intersections:
                    if np.linalg.norm(old - inter) < 1.0:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    intersections.append(inter)
        self.draw_line(img, start_x, start_y, end_x, end_y, color=(0, 255, 255), thickness=1)
        self.draw_polygons(img, polygons, color=(100, 255, 100), thickness=1)
        for inter in intersections:
            cv2.circle(img, (int(round(inter[0])), int(round(inter[1]))), 4, (0, 0, 255), -1)
        cv2.imwrite("ket_qua.jpg", img)
        if len(intersections) != 2:
            print(f"Số điểm cắt không hợp lệ: {len(intersections)} (Yêu cầu phải bằng 2)")
            return False, 0
        pixel_length = float(np.linalg.norm(intersections[0] - intersections[1]))
        print("pixel_length (Polygon):", pixel_length)
        return True, pixel_length

    def draw_line(self, image, start_x, start_y, end_x, end_y, color=(0, 255, 0), thickness=2):
        """Vẽ một đoạn thẳng đơn nối liền trực tiếp giữa hai tọa độ chỉ định lên ma trận ảnh nền.

        Args:
            image (np.ndarray): Ma trận ảnh chịu ảnh hưởng vẽ đường thẳng trực tiếp.
            start_x (numeric): Tọa độ X điểm gốc đoạn thẳng.
            start_y (numeric): Tọa độ Y điểm gốc đoạn thẳng.
            end_x (numeric): Tọa độ X điểm ngọn đoạn thẳng.
            end_y (numeric): Tọa độ Y điểm ngọn đoạn thẳng.
            color (tuple, optional): Màu sắc thiết lập nét vẽ dạng phối màu BGR. Defaults to (0, 255, 0).
            thickness (int, optional): Độ rộng pixel độ dày của đường thẳng vẽ. Defaults to 2.

        Returns:
            np.ndarray: Ảnh gốc sau khi đã chèn một đoạn thẳng vừa chỉ định vào.
        """
        cv2.line(image, (int(start_x), int(start_y)), (int(end_x), int(end_y)), color, thickness)
        return image