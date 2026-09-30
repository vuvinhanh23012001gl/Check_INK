import cv2
import numpy as np
from typing import Any
from app.engines.model_AI import ModelUnet
from shapely.geometry import LineString, Polygon
from .base_ai import BaseJudgerAI
from .base_ai import JudgmentResult

class BorderDetector(BaseJudgerAI):
    INSPECTOR_NAME = "BorderFilmInspector"

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

    def define(
        self,
        image: np.ndarray,
        lines: list[tuple[float, float, float, float]],
        Approx_value: float = 0.002,
        min_area: int = 100,
    ) -> dict[str, Any]:
        """Lấy giao điểm chính xác giữa các line và polygon UNet.

        Input: ảnh BGR, danh sách line dạng ``(x1, y1, x2, y2)`` và tham số
            hậu xử lý polygon.
        Output: dict gồm polygon dùng chung và kết quả đo của từng line.
        Errors: ``ValueError`` nếu ảnh hoặc line không hợp lệ.
        """
        if image is None or image.size == 0:
            raise ValueError("image không được rỗng")
        if not isinstance(lines, list):
            raise ValueError("lines phải là list")
        polygon = self.unet_model.get_polygon(
            image, Approx_value=Approx_value, min_area=min_area
        )
        return self.define_with_polygon(image, lines, polygon)

    def define_with_polygon(
        self,
        image: np.ndarray,
        lines: list[tuple[float, float, float, float]],
        polygon: np.ndarray | None,
    ) -> dict[str, Any]:
        """Đo các line bằng polygon đã được detector khác suy luận cùng ảnh.

        Input: Ảnh BGR, danh sách line và polygon UNet đã có.
        Output: Dict polygon, giao điểm/độ rộng từng line và ảnh đã vẽ.
        Errors: ``ValueError`` nếu ảnh rỗng hoặc ``lines`` không phải list.
        """
        if image is None or image.size == 0:
            raise ValueError("image không được rỗng")
        if not isinstance(lines, list):
            raise ValueError("lines phải là list")
        runtime_lines = self.process_lines_from_polygon(image, lines, polygon)
        return {
            "polygon": polygon,
            "lines": runtime_lines,
            "image": self._draw_result(image, polygon, runtime_lines),
        }

    def compare(self, standard_data, runtime_data, scale_mm_per_pixel: float):
        """So sánh khoảng cách đo được với chuẩn BorderFilmInspector.

        Input: ``standard_data`` là dict các item có ``widthMin``, ``widthMax``
            và có thể có ``xStart``, ``yStart``, ``xEnd``, ``yEnd``;
            ``runtime_data`` là output của ``define``; ``scale_mm_per_pixel``
            là hệ số calibration truyền từ caller.
        Output: dict kết quả từng line, gồm khoảng cách pixel, khoảng cách mm
            và trạng thái hợp lệ theo widthMin/widthMax tính bằng mm.
        Errors: ``ValueError`` nếu dữ liệu hoặc hệ số calibration không hợp lệ.
        """
        if not isinstance(scale_mm_per_pixel, (int, float)) or scale_mm_per_pixel <= 0:
            raise ValueError("scale_mm_per_pixel phải là số lớn hơn 0")
        if not isinstance(standard_data, dict):
            raise ValueError("standard_data phải là dict BorderFilmInspector")
        if not isinstance(runtime_data, dict) or "lines" not in runtime_data:
            raise ValueError("runtime_data phải là output của define")
        runtime_lines = runtime_data["lines"]
        runtime_by_index = {item["line_index"]: item for item in runtime_lines}
        comparisons = []
        items = standard_data.get("BorderFilmInspector", standard_data)
        if not isinstance(items, dict):
            raise ValueError("BorderFilmInspector phải là dict")
        for key, standard in items.items():
            if not isinstance(standard, dict):
                raise ValueError(f"Chuẩn line {key} phải là dict")
            try:
                line_index = int(key)
                width_min = float(standard["widthMin"])
                width_max = float(standard["widthMax"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Chuẩn line {key} thiếu widthMin/widthMax hợp lệ") from error
            runtime = runtime_by_index.get(line_index)
            distance_pixel = None if runtime is None else runtime["distance_pixel"]
            distance_mm = (
                None
                if distance_pixel is None
                else float(distance_pixel) * float(scale_mm_per_pixel)
            )
            is_valid = (
                runtime is not None
                and runtime["is_valid"]
                and width_min <= distance_mm <= width_max
            )
            comparisons.append({
                "line_index": line_index,
                "name_line": standard.get("nameLine") or standard.get("name_line") or str(line_index),
                "width_min": width_min,
                "width_max": width_max,
                "distance_pixel": distance_pixel,
                "distance_mm": distance_mm,
                "scale_mm_per_pixel": float(scale_mm_per_pixel),
                "runtime": runtime,
                "is_valid": is_valid,
            })
        return {
            "comparisons": comparisons,
            "polygon": runtime_data.get("polygon"),
            "image": runtime_data.get("image"),
        }

    def judge(self, comparison_data):
        """Phán định Border Film theo giới hạn min/max của từng line.

        Input: dict output của ``compare``.
        Output: ``JudgmentResult`` với ``OK`` khi tất cả line đạt chuẩn.
        Errors: ``ValueError`` nếu thiếu danh sách comparison.
        """
        if not isinstance(comparison_data, dict) or "comparisons" not in comparison_data:
            raise ValueError("comparison_data thiếu comparisons")
        comparisons = comparison_data["comparisons"]
        ok = bool(comparisons) and all(item["is_valid"] for item in comparisons)
        errors = []
        for item in comparisons:
            if not item["is_valid"]:
                runtime = item.get("runtime")
                intersection_count = (
                    0 if runtime is None else int(runtime.get("intersection_count", 0))
                )
                measured = bool(
                    runtime
                    and runtime.get("is_valid")
                    and intersection_count == 2
                    and item["distance_mm"] is not None
                )
                actual = (
                    f"{float(item['distance_mm']):g} mm"
                    if measured
                    else f"Không đo được ({intersection_count} giao điểm)"
                )
                name_line = item.get("name_line", str(item.get("line_index")))
                errors.append(
                    f"[Biên film] NG - \"{name_line}\" - "
                    f"Quy định:\"{float(item['width_min']):g} mm - "
                    f"{float(item['width_max']):g} mm\" - Thực tế :\"{actual}\""
                )
        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"line_count": len(comparisons)},
            runtime_data={"comparisons": comparisons},
            comparison_data=comparison_data,
            message="Tất cả đường biên đạt chuẩn" if ok else "Có đường biên không đạt chuẩn",
            errors=errors,
        )

    @staticmethod
    def _draw_result(
        image: np.ndarray,
        polygon: np.ndarray | None,
        lines: list[dict],
    ) -> np.ndarray:
        """Vẽ polygon, line kiểm tra và giao điểm lên ảnh output.

        Input: Ảnh BGR, polygon từ UNet và danh sách kết quả line.
        Output: Bản sao ảnh có vùng nhận diện và dữ liệu hình học.
        Errors: Không phát sinh; polygon hoặc giao điểm không hợp lệ sẽ được bỏ qua.
        """
        output = image.copy()
        if polygon is not None and len(polygon) >= 3:
            polygon_points = np.asarray(polygon).reshape(-1, 1, 2).astype(np.int32)
            cv2.polylines(output, [polygon_points], True, (0, 255, 0), 3)
        for line_data in lines:
            line = line_data.get("original_line")
            if line is None or len(line) != 4:
                continue
            start = (int(round(line[0])), int(round(line[1])))
            end = (int(round(line[2])), int(round(line[3])))
            line_color = (0, 255, 0) if line_data.get("is_valid") else (0, 0, 255)
            cv2.line(output, start, end, line_color, 2)
            for point_key in ("intersection_point_1", "intersection_point_2"):
                point = line_data.get(point_key)
                if point is not None and len(point) == 2:
                    cv2.circle(
                        output,
                        (int(round(point[0])), int(round(point[1]))),
                        6,
                        (255, 0, 0),
                        -1,
                    )
        return output

    def show(
        self,
        image: np.ndarray,
        window_name: str = "Border Detector Result"
    ) -> None:
        """Hiển thị ảnh kết quả BorderDetector bằng cửa sổ OpenCV.

        Input: ``image`` là ảnh đã được vẽ polygon, line và điểm giao;
            ``window_name`` là tên cửa sổ hiển thị.
        Output: Không trả về dữ liệu; cửa sổ chờ người dùng nhấn phím.
        Errors: ``ValueError`` nếu ảnh rỗng; ``RuntimeError`` nếu môi trường
            không hỗ trợ giao diện GUI của OpenCV.
        """
        if image is None or image.size == 0:
            raise ValueError("Ảnh BorderDetector cần hiển thị không được rỗng")
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
            cv2.waitKey(0)
        except cv2.error as error:
            raise RuntimeError(
                "Không thể hiển thị ảnh BorderDetector bằng OpenCV. "
                "Hãy chạy trong môi trường có GUI."
            ) from error
        finally:
            try:
                cv2.destroyWindow(window_name)
            except cv2.error:
                pass


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
        H, W = image.shape[:2]
        polygon = self.unet_model.get_polygon(
            image, Approx_value=Approx_value, min_area=min_area
        )
        return self.process_lines_from_polygon(image, lines, polygon)

    def process_lines_from_polygon(
        self,
        image: np.ndarray,
        lines: list,
        polygon: np.ndarray | None,
    ) -> list[dict]:
        """Đo giao điểm của từng đoạn line hữu hạn với polygon đã có.

        Input: ảnh gốc, danh sách line và polygon đã được UNet trích xuất.
        Output: danh sách số giao điểm; chỉ hai giao điểm mới có khoảng cách.
        Errors: Không phát sinh; line không hợp lệ được đánh dấu ``is_valid=False``.
        """
        results = []
        if polygon is None or len(polygon) < 3:
            print(
                "Warning: Không tìm thấy đa giác hợp lệ (hoặc ít hơn 3 đỉnh) từ ảnh."
            )
            return results
        polygon_xy = np.asarray(polygon, dtype=float).reshape(-1, 2)
        polygon_shape = Polygon(polygon_xy)
        if not polygon_shape.is_valid:
            polygon_shape = polygon_shape.buffer(0)
        if polygon_shape.is_empty:
            return results
        for idx, line in enumerate(lines):
            if len(line) != 4:
                results.append(self._invalid_line_result(idx, line))
                continue
            x1, y1, x2, y2 = map(float, line)
            dx, dy = x2 - x1, y2 - y1
            length = np.hypot(dx, dy)
            if length == 0:
                results.append(self._invalid_line_result(idx, line))
                continue
            line_segment = LineString([(x1, y1), (x2, y2)])
            geometry = line_segment.intersection(polygon_shape.boundary)
            points = self._geometry_points(geometry)
            intersection_count = len(points)
            if intersection_count == 2:
                unit_x, unit_y = dx / length, dy / length
                points.sort(key=lambda point: point[0] * unit_x + point[1] * unit_y)
                p1, p2 = points
                distance_pixel = float(np.hypot(p1[0] - p2[0], p1[1] - p2[1]))
                results.append(
                    {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": p1,
                        "intersection_point_2": p2,
                        "intersection_count": intersection_count,
                        "distance_pixel": float(distance_pixel),
                        "is_valid": True,
                    }
                )
            else:
                results.append(
                    {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": points[0] if points else None,
                        "intersection_point_2": None,
                        "intersection_count": intersection_count,
                        "distance_pixel": 0.0,
                        "is_valid": False,
                    }
                )
        return results

    @staticmethod
    def _geometry_points(geometry) -> list[tuple[float, float]]:
        """Lấy các điểm biên từ kết quả giao Shapely và loại điểm trùng."""
        points = []
        if geometry.is_empty:
            return points
        if geometry.geom_type == "Point":
            points.append((float(geometry.x), float(geometry.y)))
        elif geometry.geom_type in {"MultiPoint", "GeometryCollection"}:
            for item in geometry.geoms:
                points.extend(BorderDetector._geometry_points(item))
        elif hasattr(geometry, "coords"):
            points.extend((float(x), float(y)) for x, y in geometry.coords)
        return list(dict.fromkeys(points))

    @staticmethod
    def _invalid_line_result(index: int, line) -> dict:
        """Tạo kết quả chuẩn cho line không hợp lệ."""
        return {
            "line_index": index,
            "original_line": tuple(line) if hasattr(line, "__iter__") else line,
            "intersection_point_1": None,
            "intersection_point_2": None,
            "intersection_count": 0,
            "distance_pixel": 0.0,
            "is_valid": False,
        }