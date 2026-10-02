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
        Approx_value: float | None = None,
        min_area: int | None = None,
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
        epsilon_ratio, min_area_value = self._resolve_polygon_params(
            Approx_value,
            min_area,
        )
        mask = self.unet_model.get_mask(image)
        polygons = self._find_polygons(mask, epsilon_ratio, min_area_value)
        primary_polygon = self._select_primary_polygon(polygons)
        return self.define_with_polygon(image, lines, primary_polygon, polygons)

    def define_with_polygon(
        self,
        image: np.ndarray,
        lines: list[tuple[float, float, float, float]],
        polygon: np.ndarray | list | None,
        polygons: list[np.ndarray] | None = None,
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

        polygon_candidates = (
            self._normalize_polygons(polygons)
            if isinstance(polygons, list)
            else self._normalize_polygons(polygon)
        )
        primary_polygon = self._select_primary_polygon(polygon_candidates)
        # Đo trên toàn bộ contour candidates để tránh bỏ sót trường hợp
        # line cắt contour phụ nhưng không cắt contour lớn nhất.
        runtime_lines = self.process_lines_from_polygon(
            image,
            lines,
            polygon_candidates,
        )
        return {
            # ``polygon`` giữ contour chính để tương thích luồng cũ.
            "polygon": (
                primary_polygon.reshape(-1, 2).astype(np.int32).tolist()
                if primary_polygon is not None
                else None
            ),
            # ``polygons`` giữ toàn bộ contour theo cùng hướng với endpoint measurement master.
            "polygons": [
                contour.reshape(-1, 2).astype(np.int32).tolist()
                for contour in polygon_candidates
            ],
            "lines": runtime_lines,
            "image": self._draw_result(image, polygon_candidates, runtime_lines),
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
            intersection_count = (
                0 if runtime is None else int(runtime.get("intersection_count", 0))
            )
            distance_pixel = None if runtime is None else runtime["distance_pixel"]
            distance_mm = (
                None
                if distance_pixel is None
                else float(distance_pixel) * float(scale_mm_per_pixel)
            )
            is_valid = (
                runtime is not None
                and runtime["is_valid"]
                and intersection_count >= 2
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
            "polygons": runtime_data.get("polygons"),
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
                    and intersection_count >= 2
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
        polygons: list[np.ndarray] | None,
        lines: list[dict],
    ) -> np.ndarray:
        """Vẽ polygon, line kiểm tra và giao điểm lên ảnh output.

        Input: Ảnh BGR, polygon từ UNet và danh sách kết quả line.
        Output: Bản sao ảnh có vùng nhận diện và dữ liệu hình học.
        Errors: Không phát sinh; polygon hoặc giao điểm không hợp lệ sẽ được bỏ qua.
        """
        output = image.copy()
        if isinstance(polygons, list):
            for polygon in polygons:
                if polygon is None or len(polygon) < 3:
                    continue
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
        Approx_value: float | None = None,
        min_area: int | None = None,
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
        epsilon_ratio, min_area_value = self._resolve_polygon_params(
            Approx_value,
            min_area,
        )
        mask = self.unet_model.get_mask(image)
        polygons = self._find_polygons(mask, epsilon_ratio, min_area_value)
        polygon = self._select_primary_polygon(polygons)
        return self.process_lines_from_polygon(image, lines, polygon)

    def _resolve_polygon_params(
        self,
        approx_value: float | None,
        min_area: int | None,
    ) -> tuple[float, int]:
        """Ưu tiên tham số truyền vào, fallback về cấu hình ``UnetConfig`` của model."""
        config = getattr(self.unet_model, "config", None)
        epsilon = float(
            approx_value
            if approx_value is not None
            else getattr(config, "epsilon_ratio", 0.002)
        )
        area = int(
            min_area
            if min_area is not None
            else getattr(config, "min_area", 100)
        )
        return epsilon, max(1, area)

    @staticmethod
    def _find_polygons(
        mask: np.ndarray,
        epsilon_ratio: float,
        min_area: int,
    ) -> list[np.ndarray]:
        """Trích contour theo cùng logic ``find_polygons`` của luồng master measurement."""
        mask_u8 = np.asarray(mask, dtype=np.uint8)
        contours, _ = cv2.findContours(mask_u8, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        polygons: list[np.ndarray] = []
        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue
            epsilon = float(epsilon_ratio) * cv2.arcLength(contour, True)
            polygon = cv2.approxPolyDP(contour, epsilon, True)
            if polygon is not None and len(polygon) >= 3:
                polygons.append(polygon)
        return polygons

    @staticmethod
    def _normalize_polygons(polygon_data: np.ndarray | list | None) -> list[np.ndarray]:
        """Chuẩn hóa đầu vào polygon đơn/đa contour về list ``np.ndarray`` Nx1x2."""
        if polygon_data is None:
            return []
        if isinstance(polygon_data, np.ndarray):
            contour = np.asarray(polygon_data, dtype=np.float32).reshape(-1, 1, 2)
            if len(contour) >= 3:
                return [contour.astype(np.int32)]
            return []
        if not isinstance(polygon_data, list) or not polygon_data:
            return []

        first = polygon_data[0]
        if isinstance(first, (list, tuple, np.ndarray)) and len(first) >= 2 and not isinstance(first[0], (list, tuple, np.ndarray)):
            contour = np.asarray(polygon_data, dtype=np.float32).reshape(-1, 1, 2)
            return [contour.astype(np.int32)] if len(contour) >= 3 else []

        contours: list[np.ndarray] = []
        for candidate in polygon_data:
            try:
                contour = np.asarray(candidate, dtype=np.float32).reshape(-1, 1, 2)
            except (TypeError, ValueError):
                continue
            if len(contour) >= 3:
                contours.append(contour.astype(np.int32))
        return contours

    @staticmethod
    def _select_primary_polygon(polygons: list[np.ndarray]) -> np.ndarray | None:
        """Chọn contour chính có diện tích lớn nhất để tính giao điểm line."""
        valid = [poly for poly in polygons if isinstance(poly, np.ndarray) and len(poly) >= 3]
        if not valid:
            return None
        return max(valid, key=lambda contour: float(cv2.contourArea(contour)))

    def process_lines_from_polygon(
        self,
        image: np.ndarray,
        lines: list,
        polygon: np.ndarray | list[np.ndarray] | None,
    ) -> list[dict]:
        """Đo giao điểm của từng đoạn line hữu hạn với polygon đã có.

        Input: ảnh gốc, danh sách line và một hoặc nhiều polygon đã được UNet trích xuất.
        Output: danh sách số giao điểm; nếu có từ hai giao điểm trở lên thì
            chọn một cặp điểm đại diện theo cùng quy tắc cho mọi inspector đo.
        Errors: Không phát sinh; line không hợp lệ được đánh dấu ``is_valid=False``.
        """
        results = []
        polygon_candidates = self._normalize_polygons(polygon)
        if not polygon_candidates:
            print(
                "Warning: Không tìm thấy đa giác hợp lệ (hoặc ít hơn 3 đỉnh) từ ảnh."
            )
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
            line_midpoint = ((x1 + x2) * 0.5, (y1 + y2) * 0.5)
            selected_result: dict | None = None
            best_score: tuple[float, float] | None = None
            fallback_point: tuple[float, float] | None = None
            fallback_count = 0

            for polygon_index, polygon_item in enumerate(polygon_candidates):
                polygon_xy = np.asarray(polygon_item, dtype=float).reshape(-1, 2)
                polygon_shape = Polygon(polygon_xy)
                if not polygon_shape.is_valid:
                    polygon_shape = polygon_shape.buffer(0)
                if polygon_shape.is_empty:
                    continue

                geometry = line_segment.intersection(polygon_shape.boundary)
                points = self._geometry_points(geometry)
                intersection_count = len(points)
                if intersection_count < 2:
                    if intersection_count > 0 and fallback_point is None:
                        fallback_point = points[0]
                    fallback_count = max(fallback_count, intersection_count)
                    continue

                ordered_p1, ordered_p2 = self._select_measurement_pair(
                    points,
                    (x1, y1),
                    (x2, y2),
                    length,
                )
                distance_pixel = float(np.hypot(
                    ordered_p1[0] - ordered_p2[0],
                    ordered_p1[1] - ordered_p2[1],
                ))
                pair_midpoint = (
                    (ordered_p1[0] + ordered_p2[0]) * 0.5,
                    (ordered_p1[1] + ordered_p2[1]) * 0.5,
                )
                midpoint_distance = float(np.hypot(
                    pair_midpoint[0] - line_midpoint[0],
                    pair_midpoint[1] - line_midpoint[1],
                ))
                score = (midpoint_distance, distance_pixel)

                if best_score is None or score < best_score:
                    best_score = score
                    selected_result = {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": ordered_p1,
                        "intersection_point_2": ordered_p2,
                        "intersection_count": intersection_count,
                        "intersection_mode": (
                            "exact_pair" if intersection_count == 2 else "nearest_pair"
                        ),
                        "selected_polygon_index": polygon_index,
                        "distance_pixel": distance_pixel,
                        "is_valid": True,
                    }

            if selected_result is not None:
                results.append(selected_result)
            else:
                results.append(
                    {
                        "line_index": idx,
                        "original_line": (x1, y1, x2, y2),
                        "intersection_point_1": fallback_point,
                        "intersection_point_2": None,
                        "intersection_count": fallback_count,
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
    def _select_nearest_point_pair(
        points: list[tuple[float, float]],
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Chọn cặp giao điểm gần nhau nhất từ danh sách điểm giao.

        Input: Danh sách giao điểm biên polygon theo hệ tọa độ ảnh.
        Output: Cặp hai điểm có khoảng cách Euclid nhỏ nhất.
        Errors: ``ValueError`` nếu danh sách có ít hơn hai điểm.
        """
        if len(points) < 2:
            raise ValueError("Cần ít nhất hai điểm để chọn cặp gần nhất")
        best_pair = (points[0], points[1])
        best_distance = float(np.hypot(
            best_pair[0][0] - best_pair[1][0],
            best_pair[0][1] - best_pair[1][1],
        ))
        for index_left in range(len(points) - 1):
            left = points[index_left]
            for index_right in range(index_left + 1, len(points)):
                right = points[index_right]
                distance = float(np.hypot(left[0] - right[0], left[1] - right[1]))
                if distance < best_distance:
                    best_distance = distance
                    best_pair = (left, right)
        return best_pair

    @staticmethod
    def _select_measurement_pair(
        points: list[tuple[float, float]],
        line_start: tuple[float, float],
        line_end: tuple[float, float],
        line_length: float,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Chọn cặp điểm đo theo quy tắc chung cho mọi inspector đo.

        Input: Danh sách giao điểm biên polygon và thông tin line gốc.
        Output: Cặp điểm đã được sắp theo chiều line để đảm bảo nhất quán.
        Errors: ``ValueError`` nếu ít hơn hai giao điểm hợp lệ.
        """
        if len(points) < 2:
            raise ValueError("Cần ít nhất hai điểm giao để đo khoảng cách")

        unique_points: list[tuple[float, float]] = []
        for point in points:
            duplicated = False
            for existed in unique_points:
                if float(np.hypot(point[0] - existed[0], point[1] - existed[1])) <= 1.5:
                    duplicated = True
                    break
            if not duplicated:
                unique_points.append(point)

        candidate_points = unique_points if len(unique_points) >= 2 else points
        nearest_pair = BorderDetector._select_nearest_point_pair(candidate_points)
        min_span_threshold = max(5.0, line_length * 0.05)

        robust_pair: tuple[tuple[float, float], tuple[float, float]] | None = None
        robust_distance: float | None = None
        for index_left in range(len(candidate_points) - 1):
            left = candidate_points[index_left]
            for index_right in range(index_left + 1, len(candidate_points)):
                right = candidate_points[index_right]
                distance = float(np.hypot(left[0] - right[0], left[1] - right[1]))
                if distance < min_span_threshold:
                    continue
                if robust_distance is None or distance < robust_distance:
                    robust_distance = distance
                    robust_pair = (left, right)

        selected_pair = robust_pair if robust_pair is not None else nearest_pair
        sx, sy = line_start
        ex, ey = line_end
        dx = ex - sx
        dy = ey - sy
        projection_1 = (selected_pair[0][0] - sx) * dx + (selected_pair[0][1] - sy) * dy
        projection_2 = (selected_pair[1][0] - sx) * dx + (selected_pair[1][1] - sy) * dy
        if projection_1 <= projection_2:
            return selected_pair
        return selected_pair[1], selected_pair[0]

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