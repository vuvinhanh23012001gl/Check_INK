from .inference_unet import InferenceUnet
import numpy as np
import cv2
from skimage.morphology import skeletonize
from scipy.spatial.distance import cdist
from scipy.spatial import cKDTree
from app.config import UnetCofigAutoDetectLineMaster
import time
from collections import defaultdict

class DeploymentUnetUnet:
    def __init__(self,autoDetectLineMaster : UnetCofigAutoDetectLineMaster, infeUnet:InferenceUnet):
        self.infeUnet = infeUnet
        self.auto_detect_line_master = autoDetectLineMaster
    
    def get_mask_and_polygon(self,img):
        mask = self.infeUnet.get_mask(img)
        polygons = self.find_polygons(mask,self.infeUnet.config.epsilon_ratio,self.infeUnet.config.min_area)  #C hinh lai duong polygon
        return mask,polygons
        
    def get_mask(self,img):
        mask = self.infeUnet.get_mask(img)
        return mask

    # def automate_sampling_for_checking(self,img):
    #     height, width = img.shape[:2]
    #     mask , polygon = self.get_mask_and_polygon(img)
    #     skeleton = self.get_skeleton(mask)  # Lấy điểm dọc
    #     center_points = self.get_main_skeleton_points(skeleton)
    #     center_points = self.sample_skeleton_points(center_points, spacing = self.auto_detect_line_master.distance_between_points_center_point)  # Lấy các sample 
    #     polygon_points = self.get_polygon_points(polygon,spacing = self.auto_detect_line_master.edge_point_spacing_polygons)
    #     lines = self.extract_width_lines(polygon, polygon_points, center_points, search_length = self.auto_detect_line_master.intersection_detection_range,
    #                                      min_length = self.auto_detect_line_master.minimum_allowable_width,
    #                                      max_length = self.auto_detect_line_master.maximum_width_allowed)
    #     take_lines = self.filter_close_lines(lines,min_spacing = self.auto_detect_line_master.minimum_length_to_remove_line)
    #     lines_final = self.extend_lines(take_lines, extend_length= self.auto_detect_line_master.length_extended_at_each_end)
    #     # self.draw_points(img,center_points)
    #     # self.draw_polygons(img,polygon)
    #     # self.draw_mask(mask)
    #     # self.draw_polygon_points(img,polygon_points,radius=2,color=(255,0,0))
    #     # self.draw_lines(img,lines_final)
    #     # self.show_img(img)
    #     return lines_final,(width, height)


    def automate_sampling_for_checking(self,img,edge_point_spacing_polygons = -1,length_line_extend = -1):
        # neu  edge_point_spacing_polygons != -1 thi cho phep cau hinh tu ben ngoai
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
            spacing = self.auto_detect_line_master.distance_between_points_center_point
        )
        print(f"4. sample_skeleton_points   : {time.perf_counter() - t:.3f} s")
        t = time.perf_counter()
        spacing = (
            edge_point_spacing_polygons
            if edge_point_spacing_polygons != -1
            else self.auto_detect_line_master.edge_point_spacing_polygons
        )
        polygon_points = self.get_polygon_points(
            polygon,
            spacing = spacing
        )
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
        lines_final = self.extend_lines(
            take_lines,
            extend_length = length_line
        )
        print(f"8. extend_lines             : {time.perf_counter() - t:.3f} s")
        print(f"\n===== TOTAL: {time.perf_counter() - total_start:.3f} s =====")
        # self.draw_points(img,center_points)
        # self.draw_polygons(img,polygon)
        # self.draw_mask(mask)
        # self.draw_polygon_points(img,polygon_points,radius=2,color=(255,0,0))
        # self.draw_lines(img,lines_final)
        # self.show_img(img)
        return lines_final, (width, height),polygon
            


    def draw_lines(
        self,
        image,
        lines,
        color=(255, 255, 0),
        thickness=1
    ):
        """
        Vẽ danh sách line lên ảnh.
        Input:
            image     : ảnh cần vẽ
            lines     : danh sách line
            color     : màu line (BGR)
            thickness : độ dày line
        Output:
            image đã được vẽ line
        """
        for line in lines:

            cv2.line(
                image,
                line["p1"],
                line["p2"],
                color,
                thickness
            )
        return image
    

    def draw_polygon_points(
        self,
        image,
        polygon_points,
        radius=2,
        color=(0, 0, 255),
        thickness=-1
    ):
        """
        Vẽ các điểm sinh ra từ get_polygon_points()
        Parameters
        ----------
        image : np.ndarray
        polygon_points : list
            Output của get_polygon_points()
        radius : int
        color : tuple
            BGR
        thickness : int
        """

        for item in polygon_points:
            p = item["point"]
            x = int(round(p[0]))
            y = int(round(p[1]))
            cv2.circle(
                image,
                (x, y),
                radius,
                color,
                thickness
            )
        return image
    

    def extend_lines(
        self,
        lines,
        extend_length=10
    ):
        """
        Kéo dài các line theo cả hai đầu.
        Input:
            lines         : danh sách line
            extend_length : độ dài kéo dài thêm mỗi đầu
        Output:
            list chứa:
                p1     : điểm đầu mới
                p2     : điểm cuối mới
                length : độ dài line sau khi kéo dài
        """
        extended_lines = []

        for line in lines:

            p1 = np.array(
                line["p1"],
                dtype=np.float32
            )

            p2 = np.array(
                line["p2"],
                dtype=np.float32
            )

            direction = p2 - p1

            length = np.linalg.norm(direction)

            if length < 1:
                continue

            direction /= length

            new_p1 = p1 - direction * extend_length
            new_p2 = p2 + direction * extend_length

            extended_lines.append({
                "p1": (
                    int(round(new_p1[0])),
                    int(round(new_p1[1]))
                ),
                "p2": (
                    int(round(new_p2[0])),
                    int(round(new_p2[1]))
                ),
                "length": float(
                    np.linalg.norm(
                        new_p2 - new_p1
                    )
                )
            })

        return extended_lines
    

    def line_segment_intersection(
        self,
        p1,
        p2,
        q1,
        q2
    ):

        r = p2 - p1
        s = q2 - q1

        denom = r[0] * s[1] - r[1] * s[0]

        if abs(denom) < 1e-8:
            return None

        qp = q1 - p1

        t = (
            qp[0] * s[1]
            - qp[1] * s[0]
        ) / denom

        u = (
            qp[0] * r[1]
            - qp[1] * r[0]
        ) / denom

        # Giao điểm phải nằm trên cả 2 đoạn thẳng
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p1 + t * r

        return None
    
    def extract_width_lines(self,polygons,polygon_points,center_points,search_length=1000, min_length=5,max_length=100):
        """
        Sinh các line đo width của vật thể.
        Input:
            polygons       : danh sách polygon biên vật thể
            polygon_points : các điểm sample trên biên
            center_points  : các điểm center từ skeleton
            search_length  : khoảng dò tìm giao điểm
            min_length     : width nhỏ nhất cho phép
            max_length     : width lớn nhất cho phép

        Output:
            list chứa:
                p1     : điểm trên biên polygon
                p2     : điểm giao với biên đối diện
                length : khoảng cách từ p1 đến p2
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
            # center gần nhất
            _, idx = tree.query(p)
            center = center_points[idx].astype(np.float32)
            # vector cạnh
            edge = b - a
            edge_len = np.linalg.norm(edge)
            if edge_len < 1:
                continue
            tangent = edge / edge_len
            # pháp tuyến
            normal = np.array(
                [-tangent[1], tangent[0]],
                dtype=np.float32
            )
            # hướng pháp tuyến về center
            if np.dot(normal, center - p) < 0:
                normal *= -1
            # điểm cuối của tia dò
            ray_end = p + normal * search_length
            intersections = []
            # tìm giao điểm với tất cả cạnh polygon
            for poly2 in polygons:
                pts2 = poly2.reshape(-1, 2).astype(np.float32)
                n2 = len(pts2)
                for i in range(n2):
                    s1 = pts2[i]
                    s2 = pts2[(i + 1) % n2]
                    inter = self.line_segment_intersection(
                        p,
                        ray_end,
                        s1,
                        s2
                    )
                    if inter is None:
                        continue
                    dist = np.linalg.norm(inter - p)
                    # bỏ giao điểm tại chính P
                    if dist > 1:
                        intersections.append(
                            (dist, inter)
                        )
            if len(intersections) == 0:
                continue
            # lấy giao điểm gần nhất theo hướng normal
            intersections.sort(key=lambda x: x[0])
            length = intersections[0][0]
            p2 = intersections[0][1]
            # lọc độ dài
            if length < min_length:
                continue
            if length > max_length:
                continue
            lines.append({
                "p1": (
                    int(round(p[0])),
                    int(round(p[1]))
                ),
                "p2": (
                    int(round(p2[0])),
                    int(round(p2[1]))
                ),
                "length": float(length)
            })
        return lines

    def get_polygon_points(self,polygons,spacing=10 ):
        """
        Lấy các điểm sample trên biên polygon.
        Input:
            polygons : danh sách polygon
            spacing  : khoảng cách giữa các điểm

        Output:
            list chứa:
                point    : tọa độ điểm
                poly_idx : polygon chứa điểm
                edge_idx : cạnh chứa điểm
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


    def draw_points(
            self,
            img,
            points,
            radius=2,
            color=(0, 0, 255),
            thickness=-1
        ):
            """
            Vẽ các điểm lên ảnh

            Parameters
            ----------
            img : np.ndarray
                Ảnh BGR

            points : np.ndarray
                [[x,y], [x,y], ...]

            radius : int
                Bán kính điểm

            color : tuple
                Màu BGR

            thickness : int
                -1 => tô kín
            """

            for x, y in points:
                cv2.circle(
                    img,
                    (int(x), int(y)),
                    radius,
                    color,
                    thickness
                )

            return img
    


    def sample_skeleton_points(self,
    points,
            spacing=10
        ):
            """
            Lấy các điểm skeleton theo khoảng cách cố định.
            Input:
                points  : danh sách điểm skeleton đã sắp xếp
                spacing : khoảng cách giữa các điểm sample
            Output:
                mảng các điểm skeleton đã được lấy mẫu
            """

            if len(points) < 2:
                return points

            sampled = [points[0]]

            accumulated = 0

            for i in range(1, len(points)):

                d = np.linalg.norm(
                    points[i] - points[i - 1]
                )

                accumulated += d

                if accumulated >= spacing:
                    sampled.append(points[i])
                    accumulated = 0

            return np.array(sampled)

    def get_main_skeleton_points(self, skeleton):
        #     Sắp xếp các điểm skeleton theo thứ tự dọc theo đường xương sống.
        #     Input:
        #         skeleton : ảnh skeleton
        #     Output:
        #         mảng điểm skeleton đã được sắp xếp
        #     """
        ys, xs = np.where(skeleton > 0)
        points = np.column_stack((xs, ys)).astype(np.float32)

        n = len(points)

        if n < 2:
            return points

        # Tìm điểm bắt đầu
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

    def get_skeleton(self,mask):
            """
            Tạo skeleton từ mask.
            Input:
                mask : ảnh mask nhị phân
            Output:
                ảnh skeleton
            """
            skeleton = skeletonize(mask > 0)
            return skeleton.astype(np.uint8)
    
    def get_skeleton_points(self,skeleton):
            """
            Lấy tọa độ các điểm trên skeleton.
            Input:
                skeleton : ảnh skeleton
            Output:
                mảng điểm [x, y]
            """
            ys, xs = np.where(skeleton > 0)
            points = np.column_stack((xs, ys))
            return points
    


    def clean_mask_opening(self, mask, kernel_size=3, iterations=1):
        """
            Làm sạch mask bằng phép Morphology Opening (Erosion + Dilation)
            Parameters:
                mask (np.ndarray): Ảnh mask nhị phân (0 hoặc 255)
                kernel_size (int): Kích thước kernel (ví dụ: 3 → kernel 3x3)
                iterations (int): Số lần lặp phép morphology
            Returns:
                np.ndarray: Mask đã được làm sạch
        """
        mask = mask.astype(np.uint8)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask_clean = cv2.morphologyEx(
                mask,
                cv2.MORPH_OPEN,
                kernel,
                iterations=iterations
            )
        return mask_clean
    

    def draw_mask(self, mask, window_name="Mask"):
        """
        Hiển thị mask đơn giản
        """
        mask = mask.astype(np.uint8)
        cv2.imshow(window_name, mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def show_img(self,image, window_name="Image"):
        """Hiển thị ảnh CV2"""
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    
    def find_polygons(
        self,
        mask,
        epsilon_ratio=0.002,
        min_area=100
    ):
        """
        Tìm tất cả polygon trong mask.

        Parameters
        ----------
        mask : np.ndarray
            Mask nhị phân (0 hoặc 255)

        epsilon_ratio : float
            Tỷ lệ xấp xỉ polygon

        min_area : int
            Diện tích tối thiểu của contour

        Returns
        -------
        list[np.ndarray]
            Danh sách polygon
        """
        mask = mask.astype(np.uint8)
        contours, hierarchy = cv2.findContours(
            mask,
            cv2.RETR_TREE,          # Lấy cả contour ngoài và trong
            cv2.CHAIN_APPROX_NONE
        )
        polygons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            epsilon = epsilon_ratio * cv2.arcLength(cnt, True)
            poly = cv2.approxPolyDP(
                cnt,
                epsilon,
                True
            )
            polygons.append(poly)
        return polygons
    
    def draw_polygons( self,image,polygons,color=(0,255,0), thickness=2):
        """
        Vẽ danh sách polygon lên ảnh.

        Input:
            image     : ảnh cần vẽ
            polygons  : danh sách polygon
            color     : màu đường viền (BGR)
            thickness : độ dày nét vẽ

        Output:
            image đã được vẽ polygon
        """
        for poly in polygons:
            cv2.polylines(
                image,
                [poly],
                True,
                color,
                thickness
            )

        return image
    


    def filter_close_lines(self, lines, min_spacing=20):
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

            # nếu cắt nhau
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
            """
            Kiểm tra line cắt vật thể dựa trên các cạnh của POLYGON.
            Đồng thời vẽ các điểm cắt tìm thấy lên màn hình để debug.
            """
            mask = self.infeUnet.get_mask(img)
            cv2.circle(img,(start_x, start_y), 4, (0, 255, 255),-1)
            cv2.circle(img,(end_x, end_y), 4, (0, 255, 255),-1)
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
                cv2.circle(
                    img, 
                    (int(round(inter[0])), int(round(inter[1]))), 
                    4,          
                    (0, 0, 255),
                    -1        
                )
            cv2.imwrite("ket_qua.jpg", img)
            if len(intersections) != 2:
                print(f"Số điểm cắt không hợp lệ: {len(intersections)} (Yêu cầu phải bằng 2)")
                #self.show_img(img)
                return False, 0
            pixel_length = float(np.linalg.norm(intersections[0] - intersections[1]))
            print("pixel_length (Polygon):", pixel_length)
            #self.show_img(img)
            return True, pixel_length


    def draw_line(self, image, start_x, start_y, end_x, end_y, color=(0, 255, 0), thickness=2):
        """ Vẽ một đoạn thẳng """
        cv2.line(
            image,
            (int(start_x), int(start_y)),
            (int(end_x), int(end_y)),
            color,
            thickness
        )
        return image