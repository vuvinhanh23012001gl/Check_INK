from app.engines.AI_model_process import FrameModelYoloSegment
from shapely.geometry import Polygon
import cv2
import numpy as np
from typing import Optional, List, Tuple, Dict
from .base_ai import BaseJudgerAI, JudgmentResult

class SemiPermeableMembrane(BaseJudgerAI):
    INSPECTOR_NAME = "MembraneInspector"

    # Lớp này lấy dữ liệu 
    #Lớp này nhận
    def __init__(self, border_semi_permeable_membrane: FrameModelYoloSegment, inner_semi_permeable_membrane: FrameModelYoloSegment):
        super().__init__()
        self.border_semi_permeable_membrane = border_semi_permeable_membrane
        self.inner_semi_permeable_membrane = inner_semi_permeable_membrane

    def define(
        self,
        img: np.ndarray,
        x1: int,
        y1: int,
        x2: int,
        y2: int
    ) -> Tuple[bool, Optional[List[Tuple[float, float]]], np.ndarray]:
        """
        Thực hiện suy luận segmentation cho hai lớp màng (border và inner), kiểm tra
        xem màng inner có nằm hoàn toàn trong màng border hay không, đồng thời
        trực quan hóa kết quả lên ảnh đầu vào.
        Quy trình xử lý:
        1. Dùng model segmentation để lấy mask/polygon cho border và inner.
        2. Trích xuất polygon đại diện cho class đầu tiên của mỗi nhóm segment.
        3. Kiểm tra quan hệ hình học bằng Shapely (contains).
        4. Nếu inner không nằm hoàn toàn trong border, tính các điểm giao nhau.
        5. Vẽ polygon và các điểm lỗi lên ảnh.
        6. Hiển thị kết quả trực quan.
        Args:
            img (np.ndarray): Ảnh đầu vào.
            x1 (int): Tọa độ x góc trên trái của vùng ROI.
            y1 (int): Tọa độ y góc trên trái của vùng ROI.
            x2 (int): Tọa độ x góc dưới phải của vùng ROI.
            y2 (int): Tọa độ y góc dưới phải của vùng ROI.
        Returns:
            Tuple[bool, Optional[List[Tuple[float, float]]], np.ndarray]:
                - True, None, image: inner nằm hoàn toàn trong border.
                - False, List[(x, y)], image: inner không nằm hoàn toàn trong border
                và trả về các điểm giao giữa hai polygon (nếu có).
                - False, None, image: không phát hiện được polygon hợp lệ hoặc lỗi xử lý.
        Side Effects:
            - In log trạng thái ra console.
            - Hiển thị ảnh kết quả bằng OpenCV window.
        """
        segments_boder = self.border_semi_permeable_membrane.get_segments(img, x1, y1, x2, y2)
        segments_inner = self.inner_semi_permeable_membrane.get_segments(img, x1, y1, x2, y2)
        polygon_border = self.get_first_class_polygon(segments_boder)
        polygon_innner = self.get_first_class_polygon(segments_inner)
        status, data = self.check_inner_completely_inside(polygon_border, polygon_innner)
        img_visualized = self.draw_membranes(img, polygon_border, polygon_innner)
        if data:
            img_visualized = self.draw_intersection_points(img_visualized, data)
        print(f"Trạng thái (Nằm hoàn toàn trong): {status}")
        print(f"Các điểm cắt lỗi: {data}")
        # self.show_image(img_visualized, window_name="Membrane Judgment Result")
        return status, data,img_visualized

    def compare(self, standard_data, runtime_data):
        """Kiểm tra luật inner phải nằm hoàn toàn trong border.

        Input: ``standard_data`` phải là ``True`` vì đây là luật cố định;
            ``runtime_data`` là tuple ``(status, intersection_points, image)``.
        Output: dict chứa trạng thái hình học, các điểm giao và ảnh kết quả.
        Errors: ``ValueError`` nếu chuẩn hoặc runtime không đúng cấu trúc.
        """
        if standard_data is not True:
            raise ValueError("standard_data của màng bán thấm phải là True")
        if not isinstance(runtime_data, tuple) or len(runtime_data) != 3:
            raise ValueError("runtime_data phải là tuple (status, data, image)")
        runtime_status, intersection_points, image = runtime_data
        if not isinstance(runtime_status, bool):
            raise ValueError("status trong runtime_data phải là bool")
        if intersection_points is not None and not isinstance(intersection_points, list):
            raise ValueError("intersection_points phải là list hoặc None")
        return {
            "required_inside": True,
            "runtime_inside": runtime_status,
            "intersection_points": intersection_points,
            "image": image,
        }

    def judge(self, comparison_data):
        """Phán định quan hệ hình học giữa inner và border.

        Input: dict kết quả từ ``compare``.
        Output: ``JudgmentResult`` với trạng thái ``OK`` khi inner nằm hoàn
            toàn trong border, ngược lại là ``NG``.
        Errors: ``ValueError`` nếu thiếu dữ liệu bắt buộc.
        """
        required_keys = {"required_inside", "runtime_inside", "intersection_points"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu màng bán thấm bắt buộc")
        ok = (
            comparison_data["required_inside"] is True
            and comparison_data["runtime_inside"] is True
        )
        errors = []
        if not ok:
            intersection_points = comparison_data.get("intersection_points")
            if intersection_points and len(intersection_points) > 0:
                thuc_te = f"Đường viền trong cắt ra ngoài đường viền ngoài ({len(intersection_points)} điểm giao)"
            elif intersection_points is None:
                thuc_te = "Không xác định đủ đường viền trong và ngoài"
            else:
                thuc_te = "Đường viền trong nằm ngoài đường viền ngoài"

            errors.append(
                f"[Màng bán thấm] NG - \"Màng\" - "
                f"Quy định:\"Đường viền trong nằm trong đường viền ngoài\" - "
                f"Thực tế :\"{thuc_te}\""
            )
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"inner_completely_inside_border": True},
            runtime_data={
                "inner_completely_inside_border": comparison_data["runtime_inside"],
                "intersection_points": comparison_data["intersection_points"],
            },
            comparison_data=comparison_data,
            message=(
                "Màng bám thấm đạt chuẩn"
                if ok
                else "Màng bám thấm không đạt chuẩn"
            ),
            errors=errors,
        )


    def get_first_class_polygon(self, segments: List[Dict]) -> Optional[np.ndarray]:
        """
        Trích xuất polygon đầu tiên thuộc class xuất hiện đầu tiên trong danh sách
        segmentation results.
        Hàm sẽ:
        - Lấy class_id của phần tử đầu tiên trong danh sách segments.
        - Tìm tất cả segment có cùng class_id đó.
        - Trả về polygon của segment đầu tiên khớp.
        Args:
            segments (List[Dict]):
                Danh sách kết quả segmentation, mỗi dict chứa:
                - "class_id": ID của lớp
                - "polygon": danh sách tọa độ [(x, y), ...]
        Returns:
            Optional[np.ndarray]:
                - Mảng numpy shape (N, 2) biểu diễn polygon nếu tồn tại.
                - None nếu danh sách rỗng hoặc không hợp lệ.
        Notes:
            - Hàm giả định segments đã được sắp xếp theo độ tin cậy hoặc thứ tự
            ưu tiên từ model.
        """
        if not segments:
            return None
        first_class_id = segments[0]["class_id"]
        for seg in segments:
            if seg["class_id"] == first_class_id:
                return np.array(seg["polygon"], dtype=np.int32)
        return None


    def check_inner_completely_inside(self, polygon_border: Optional[np.ndarray], polygon_inner: Optional[np.ndarray]) -> Tuple[bool, Optional[List[Tuple[float, float]]]]:
        """
        Kiểm tra `polygon_inner` có nằm hoàn toàn trong `polygon_border` hay không.
        Args:
            polygon_border (Optional[np.ndarray]): Polygon bao ngoài.
            polygon_inner (Optional[np.ndarray]): Polygon cần kiểm tra.
        Returns:
            Tuple[bool, Optional[List[Tuple[float, float]]]]:
                - (True, None): `polygon_inner` nằm hoàn toàn trong `polygon_border`.
                - (False, List[Tuple[float, float]]): Không nằm hoàn toàn trong và trả về các điểm giao biên (nếu có).
                - (False, None): Dữ liệu đầu vào không hợp lệ hoặc xảy ra lỗi.
        """
        if polygon_border is None or polygon_inner is None:
            print("[WARNING] Một trong hai hoặc cả hai polygon đều rỗng (None).")
            return False, None
        if len(polygon_border) < 3 or len(polygon_inner) < 3:
            print("[WARNING] Polygon không đủ số điểm (tối thiểu cần 3 điểm).")
            return False, None
        try:
            poly_border = Polygon(polygon_border)
            poly_inner = Polygon(polygon_inner)
            if not poly_border.is_valid:
                poly_border = poly_border.buffer(0)
            if not poly_inner.is_valid:
                poly_inner = poly_inner.buffer(0)

            is_inside = poly_border.contains(poly_inner)
            if is_inside:
                return True, None
            intersection_line = poly_border.boundary.intersection(poly_inner.boundary)
            intersection_points = []

            if not intersection_line.is_empty:
                if hasattr(intersection_line, "geoms"):
                    for geom in intersection_line.geoms:
                        if geom.geom_type == "Point":
                            intersection_points.append((geom.x, geom.y))
                        elif hasattr(geom, "coords"):
                            intersection_points.extend(list(geom.coords))
                elif intersection_line.geom_type == "Point":
                    intersection_points.append((intersection_line.x, intersection_line.y))
                elif hasattr(intersection_line, "coords"):
                    intersection_points.extend(list(intersection_line.coords))

            unique_points = list(dict.fromkeys(intersection_points))
            return False, unique_points

        except Exception as e:
            print(f"[ERROR] Lỗi khi xử lý hình học Shapely: {e}")
            return False, None


    def draw_intersection_points(self, image: np.ndarray, points: List[Tuple[float, float]], color: Tuple[int, int, int] = (0, 0, 255), radius: int = 5, thickness: int = -1) -> np.ndarray:
        """
        Vẽ các điểm giao (các điểm lỗi hình học) lên ảnh.
        Mỗi điểm được vẽ thành:
        - Một chấm tròn màu chính (mặc định đỏ).
        - Một viền trắng bao quanh để dễ quan sát.
        Args:
            image (np.ndarray):
                Ảnh đầu vào.
            points (List[Tuple[float, float]]):
                Danh sách tọa độ điểm giao cần vẽ.
            color (Tuple[int, int, int], optional):
                Màu điểm theo định dạng BGR (mặc định đỏ).
            radius (int, optional):
                Bán kính vòng tròn chính.
            thickness (int, optional):
                Độ dày nét vẽ (-1 = tô đầy).
        Returns:
            np.ndarray:
                Ảnh đã được vẽ thêm các điểm giao.
        Notes:
            - Ảnh gốc không bị thay đổi (copy trước khi vẽ).
            - Tọa độ float sẽ được làm tròn về int.
        """
        image_draw = image.copy()

        if not points:
            return image_draw

        for pt in points:
            center_coordinates = (int(round(pt[0])), int(round(pt[1])))
            cv2.circle(image_draw, center_coordinates, radius=radius, color=color, thickness=thickness)
            cv2.circle(image_draw, center_coordinates, radius=radius + 3, color=(255, 255, 255), thickness=1)

        return image_draw

    def draw_membranes(self, image: np.ndarray, polygon_border: Optional[np.ndarray], polygon_inner: Optional[np.ndarray], border_color: Tuple[int, int, int] = (255, 0, 0), inner_color: Tuple[int, int, int] = (0, 255, 255), thickness: int = 2) -> np.ndarray:
        """
        Vẽ hai polygon (border và inner) lên ảnh để trực quan hóa kết quả.
        Args:
            image (np.ndarray):
                Ảnh đầu vào.
            polygon_border (Optional[np.ndarray]):
                Polygon của màng border (N, 2).
            polygon_inner (Optional[np.ndarray]):
                Polygon của màng inner (M, 2).
            border_color (Tuple[int, int, int], optional):
                Màu đường viền border (BGR).
            inner_color (Tuple[int, int, int], optional):
                Màu đường viền inner (BGR).
            thickness (int, optional):
                Độ dày đường vẽ.
        Returns:
            np.ndarray:
                Ảnh đã được vẽ hai polygon.
        Notes:
            - Polygon phải có ít nhất 3 điểm mới được vẽ.
            - Không modify ảnh gốc (copy trước khi xử lý).
        """
        image_draw = image.copy()
        if polygon_border is not None and len(polygon_border) >= 3:
            pts_border = np.asarray(polygon_border, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(image_draw, [pts_border], isClosed=True, color=border_color, thickness=thickness)

        if polygon_inner is not None and len(polygon_inner) >= 3:
            pts_inner = np.asarray(polygon_inner, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(image_draw, [pts_inner], isClosed=True, color=inner_color, thickness=thickness)

        return image_draw

    def show_image(self, image: np.ndarray, window_name: str = "Image Viewer", delay: int = 0) -> None:
        """
        Hiển thị ảnh bằng OpenCV trong cửa sổ có thể resize.
        Chức năng:
        - Tạo window hiển thị ảnh.
        - Tự động scale nếu ảnh quá lớn.
        - Hiển thị ảnh và chờ phím nhấn (hoặc theo delay).
        - Giải phóng tài nguyên cửa sổ sau khi hiển thị.
        Args:
            image (np.ndarray):
                Ảnh cần hiển thị.
            window_name (str, optional):
                Tên cửa sổ hiển thị.
            delay (int, optional):
                Thời gian chờ cv2.waitKey():
                - 0: chờ người dùng nhấn phím
                - >0: delay theo ms
        Returns:
            None
        Notes:
            - Nếu ảnh rỗng sẽ không hiển thị.
            - Luôn gọi destroyWindow để tránh leak tài nguyên GUI.
            - Có xử lý exception để tránh crash chương trình.
        """
        if image is None or image.size == 0:
            print(f"[ERROR] Không thể hiển thị ảnh '{window_name}' vì dữ liệu trống.")
            return

        try:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

            height, width = image.shape[:2]
            max_width = 1200

            if width > max_width:
                scale = max_width / width
                cv2.resizeWindow(window_name, int(width * scale), int(height * scale))
            else:
                cv2.resizeWindow(window_name, width, height)

            cv2.imshow(window_name, image)
            cv2.waitKey(delay)

        except Exception as e:
            print(f"[ERROR] Gặp lỗi khi hiển thị bằng OpenCV: {e}")

        finally:
            try:
                cv2.destroyWindow(window_name)
            except cv2.error:
                # Cửa sổ có thể chưa được tạo hoặc đã bị đóng bởi người dùng.
                pass