from app.engines.AI_model_process import FrameModelYoloObject
import numpy as np
from collections.abc import Mapping
from typing import Any, Tuple
from app.config import ClassNameModelSurfaceConfig
from .base_ai import BaseJudgerAI, JudgmentResult

class WeldSeamAirBubbles(BaseJudgerAI):
    INSPECTOR_NAME = "AirBubblesItemInspector"

    def __init__(
        self,
        model_bubble: FrameModelYoloObject,
        weld_seam_service: Any | None = None,
    ):
        super().__init__()
        self.model_bubble = model_bubble
        self.weld_seam_service = weld_seam_service

    def set_weld_seam_service(self, weld_seam_service: Any | None) -> None:
        """Cập nhật service UNet/skeleton dùng cho fallback polygon runtime.

        Input: service có hàm ``extract_weld_seam_reference(img)`` hoặc ``None``.
        Output: Không trả về dữ liệu.
        Errors: Không phát sinh.
        """
        self.weld_seam_service = weld_seam_service

    def define(
        self,
        img: np.ndarray,
        bounding_box_abnormal: list,
        weld_polygon: list = None,
        weld_skeleton_points: list | None = None,
    ) -> Tuple[bool, list[str], np.ndarray, dict[str, Any]]:
            """
            Quét bọt khí độc lập trên từng vùng cấm đã cấu hình và kiểm tra phân loại đường hàn.
            Args:
                img (np.ndarray): Ảnh gốc đầu vào.
                bounding_box_abnormal: Danh sách vùng dạng tuple
                    ``(x, y, width, height)`` hoặc dict có ``xStart``, ``yStart``,
                    ``xEnd``, ``yEnd``.
                weld_polygon: Đa giác đường hàn (nếu có) để phân loại bọt khí nằm trong hay ngoài.
                weld_skeleton_points: Danh sách điểm skeleton runtime đã có sẵn
                    (từ weld reference hoặc inspector trước đó) để vẽ trực tiếp.
            Returns:
                Tuple[bool, list[str], np.ndarray]:
                    - bool: True nếu TẤT CẢ các vùng kiểm tra đều sạch (Đạt), False nếu có BẤT KỲ vùng nào lỗi (Lỗi).
                    - list[str]: Danh sách tổng hợp tin nhắn log từ tất cả các vùng kiểm tra.
                    - np.ndarray: Ảnh kết quả cuối cùng (đã được vẽ tất cả các bọt khí/vật thể lỗi nếu có).
            """
            if img is None or img.size == 0:
                raise ValueError("Ảnh đầu vào không được rỗng")
            if not isinstance(bounding_box_abnormal, list):
                raise ValueError("bounding_box_abnormal phải là list")
            if not bounding_box_abnormal:
                success_msg = "OK: Không có vùng kiểm tra bọt khí nào được cấu hình."
                return True, [success_msg], img

            runtime_polygon, skeleton_points, polygon_source = self._resolve_runtime_polygon(
                img,
                weld_polygon,
                weld_skeleton_points,
            )
            weld_contour = self._to_main_contour(runtime_polygon)
            has_polygon = weld_contour is not None

            import cv2
            normalized_regions = self._normalize_regions(bounding_box_abnormal)
            all_messages = []
            is_all_valid = True
            img_output = img.copy()  # Tạo bản sao để vẽ đè kết quả lỗi qua từng vòng lặp
            inside_total = 0
            outside_total = 0
            bubble_total = 0
            detected_objects_all: list[dict[str, Any]] = []

            for idx, box in enumerate(normalized_regions):
                xyxy = self._xywh_to_xyxy(box)
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                all_messages.append(f"--- Kiểm tra vùng bọt khí #{idx + 1} tại [{x1}, {y1}, {x2}, {y2}] ---")

                # Lấy tất cả đối tượng trong vùng một cách an toàn
                res_obj = self.model_bubble.get_objects(img_output, x1, y1, x2, y2)
                all_objects = res_obj[0] if isinstance(res_obj, (tuple, list)) and len(res_obj) > 0 else []

                res_filter = self.model_bubble.filter_objects_by_class_name(
                    all_objects, ClassNameModelSurfaceConfig.AIR_BUBBLE.value
                )
                if isinstance(res_filter, (tuple, list)) and len(res_filter) >= 2:
                    bubble_objects, is_exist = res_filter[0], res_filter[1]
                else:
                    bubble_objects = res_filter[0] if isinstance(res_filter, (tuple, list)) and len(res_filter) > 0 else []
                    is_exist = len(bubble_objects) > 0


                if is_exist:
                    is_all_valid = False
                    inside_count = 0
                    outside_count = 0
                    bubble_total += len(bubble_objects)
                    for obj in bubble_objects:
                        bbox = obj.get("bbox", {})
                        if bbox and "x1" in bbox and "y1" in bbox:
                            cx = (bbox["x1"] + bbox["x2"]) / 2.0
                            cy = (bbox["y1"] + bbox["y2"]) / 2.0
                            if has_polygon:
                                dist = cv2.pointPolygonTest(weld_contour, (float(cx), float(cy)), False)
                                is_inside = dist >= 0
                                obj["is_inside_weld"] = bool(is_inside)
                                obj["location_text"] = (
                                    "Trong đường hàn" if is_inside else "Ngoài đường hàn"
                                )
                            else:
                                is_inside = None
                                obj["is_inside_weld"] = None
                                obj["location_text"] = "Chưa phán định (thiếu polygon runtime)"
                            if is_inside:
                                inside_count += 1
                            elif is_inside is False:
                                outside_count += 1
                    detected_objects_all.extend(bubble_objects)

                    if not has_polygon:
                        all_messages.append(
                            "CẢNH BÁO: Thiếu polygon runtime, chỉ phát hiện bọt khí, không phân loại trong/ngoài đường hàn."
                        )
                    elif inside_count > 0 and outside_count == 0:
                        all_messages.append(f"LỖI: Phát hiện {inside_count} bọt khí trong đường hàn.")
                    elif outside_count > 0 and inside_count == 0:
                        all_messages.append(f"CẢNH BÁO: Phát hiện {outside_count} bọt khí ngoài đường hàn.")
                    else:
                        all_messages.append(f"LỖI: Phát hiện {inside_count} bọt khí trong đường hàn, {outside_count} bọt khí ngoài đường hàn.")
                    inside_total += inside_count
                    outside_total += outside_count

                    # Vẽ bọt khí và vùng ROI
                    img_output = self.model_bubble.draw(img_output, bubble_objects)
                    cv2.rectangle(img_output, (x1, y1), (x2, y2), (255, 0, 0), 2)
                else:
                    if has_polygon:
                        all_messages.append("OK: Vùng kiểm tra đạt chuẩn. Không phát hiện bọt khí.")
                    else:
                        all_messages.append(
                            "CẢNH BÁO: Thiếu polygon runtime, không có bọt khí phát hiện và không phân loại vị trí."
                        )

            draw_polygon_for_air_bubble = (
                has_polygon and polygon_source != "shared_from_measurement_or_slit"
            )
            if draw_polygon_for_air_bubble and weld_contour is not None:
                cv2.polylines(img_output, [weld_contour.astype(np.int32)], True, (0, 255, 0), 2)
            if skeleton_points:
                for point in skeleton_points:
                    if not isinstance(point, (list, tuple)) or len(point) < 2:
                        continue
                    cv2.circle(
                        img_output,
                        (int(point[0]), int(point[1])),
                        1,
                        (0, 255, 255),
                        -1,
                    )

            metadata = {
                "has_runtime_polygon": has_polygon,
                "missing_runtime_polygon": not has_polygon,
                "polygon_source": polygon_source,
                "inside_count": inside_total,
                "outside_count": outside_total,
                "bubble_count": bubble_total,
                "skeleton_points": skeleton_points,
                "objects": detected_objects_all,
                "polygon": runtime_polygon,
                "draw_polygon_for_air_bubble": draw_polygon_for_air_bubble,
            }

            return is_all_valid, all_messages, img_output, metadata


    def compare(self, standard_data, runtime_data):
        """So sánh luật cấm bọt khí với kết quả quét runtime.

        Input: ``standard_data`` phải là ``True``; ``runtime_data`` là tuple
            ``(status, messages, image)`` từ ``define``.
        Output: dict chứa trạng thái vùng không có bọt khí.
        Errors: ``ValueError`` nếu dữ liệu không đúng cấu trúc.
        """
        if standard_data is not True:
            raise ValueError("standard_data của bọt khí phải là True")
        if not isinstance(runtime_data, tuple) or len(runtime_data) not in {3, 4}:
            raise ValueError("runtime_data phải là tuple (status, messages, image[, metadata])")
        runtime_clean, messages, image = runtime_data[:3]
        metadata = runtime_data[3] if len(runtime_data) == 4 else {}
        if not isinstance(runtime_clean, bool):
            raise ValueError("status trong runtime_data phải là bool")
        if not isinstance(messages, list):
            raise ValueError("messages trong runtime_data phải là list")
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValueError("metadata trong runtime_data phải là dict")
        return {
            "air_bubble_forbidden": True,
            "runtime_clean": runtime_clean,
            "messages": messages,
            "image": image,
            "has_runtime_polygon": bool(metadata.get("has_runtime_polygon", False)),
            "missing_runtime_polygon": bool(metadata.get("missing_runtime_polygon", False)),
            "polygon_source": metadata.get("polygon_source"),
            "inside_count": int(metadata.get("inside_count", 0)),
            "outside_count": int(metadata.get("outside_count", 0)),
            "bubble_count": int(metadata.get("bubble_count", 0)),
            "skeleton_points": metadata.get("skeleton_points") or [],
            "objects": metadata.get("objects") or [],
            "polygon": metadata.get("polygon"),
            "draw_polygon_for_air_bubble": bool(
                metadata.get("draw_polygon_for_air_bubble", False)
            ),
        }

    def judge(self, comparison_data):
        """Phán định bọt khí theo vị trí tương đối với đường hàn.

        Input: ``comparison_data`` là dict đầu ra từ ``compare``.
        Output: ``JudgmentResult`` với quy tắc:
            - Có bọt khí trong đường hàn: ``NG``.
            - Chỉ có bọt khí ngoài đường hàn: ``OK`` kèm cảnh báo.
            - Không phát hiện bọt khí: ``OK``.
            - Thiếu polygon runtime: ``OK`` theo nguyên tắc hiện tại.
        Errors: ``ValueError`` nếu thiếu dữ liệu bắt buộc.
        """
        required_keys = {"air_bubble_forbidden", "runtime_clean", "messages"}
        if not required_keys.issubset(comparison_data):
            raise ValueError("comparison_data thiếu dữ liệu bọt khí bắt buộc")

        if comparison_data.get("missing_runtime_polygon"):
            return JudgmentResult(
                ok=True,
                status="OK",
                standard_data={"air_bubble_forbidden": True},
                runtime_data={
                    "air_bubble_found": comparison_data.get("bubble_count", 0) > 0,
                    "messages": comparison_data.get("messages", []),
                    "missing_judgment_data": False,
                    "missing_reason": "runtime_polygon_missing",
                    "bubble_count": comparison_data.get("bubble_count", 0),
                    "polygon_source": comparison_data.get("polygon_source"),
                    "skeleton_points": comparison_data.get("skeleton_points", []),
                    "objects": comparison_data.get("objects", []),
                },
                comparison_data=comparison_data,
                message=(
                    "Không có polygon runtime để phân loại vị trí bọt khí; "
                    "kết quả tạm thời OK theo nguyên tắc hiện tại."
                ),
                errors=[],
            )

        has_inside = comparison_data.get("inside_count", 0) > 0
        has_outside = comparison_data.get("outside_count", 0) > 0

        if has_inside:
            ok = False
        elif has_outside:
            ok = True
        else:
            ok = (
                comparison_data["air_bubble_forbidden"] is True
                and comparison_data["runtime_clean"] is True
            )

        errors = []
        if not ok:
            if has_inside and has_outside:
                actual = "Phát hiện bọt khí trong và ngoài đường hàn"
            elif has_inside:
                actual = "Phát hiện bọt khí trong đường hàn"
            elif has_outside:
                actual = "Phát hiện bọt khí ngoài đường hàn"
            else:
                actual = "Phát hiện bọt khí"

            errors.append(
                f"🔵 [Bọt khí đường hàn] NG - \"Bọt khí\" - Quy định:\"Không có bọt khí\" - Thực tế :\"{actual}\""
            )
        elif has_outside:
            actual = "Phát hiện bọt khí ngoài đường hàn"
        else:
            actual = "Không phát hiện bọt khí"

        return JudgmentResult(
            ok=ok,
            status="OK" if ok else "NG",
            standard_data={"air_bubble_forbidden": True},
            runtime_data={
                "air_bubble_found": not comparison_data["runtime_clean"],
                "messages": comparison_data["messages"],
                "missing_judgment_data": False,
                "inside_count": comparison_data.get("inside_count", 0),
                "outside_count": comparison_data.get("outside_count", 0),
            },
            comparison_data=comparison_data,
            message=(
                "Phát hiện bọt khí ngoài đường hàn, kết quả OK (cảnh báo)."
                if ok and has_outside
                else "Không phát hiện bọt khí"
                if ok
                else f"{actual}, kết quả NG"
            ),
            errors=errors,
        )

    @staticmethod
    def _to_main_contour(weld_polygon: list | None) -> np.ndarray | None:
        """Chuẩn hóa polygon list thành contour chính phục vụ pointPolygonTest.

        Input: polygon list có thể là contour đơn hoặc list nhiều contour.
        Output: np.ndarray dạng contour chính hoặc ``None`` nếu không hợp lệ.
        Errors: Không phát sinh.
        """
        if not weld_polygon or not isinstance(weld_polygon, list):
            return None
        try:
            if (
                len(weld_polygon) > 0
                and isinstance(weld_polygon[0], list)
                and weld_polygon[0]
                and isinstance(weld_polygon[0][0], list)
            ):
                main_poly = max(
                    weld_polygon,
                    key=lambda pts: len(pts) if isinstance(pts, list) else 0,
                )
            else:
                main_poly = weld_polygon
            contour = np.array(main_poly, dtype=np.int32)
            return contour if len(contour) >= 3 else None
        except Exception:
            return None

    def _resolve_runtime_polygon(
        self,
        img: np.ndarray,
        weld_polygon: list | None,
        weld_skeleton_points: list | None = None,
    ) -> tuple[list | None, list, str]:
        """Lấy polygon runtime theo thứ tự ưu tiên shared -> fallback UNet/skeleton.

        Input: ảnh runtime và polygon chia sẻ nếu có.
        Output: (polygon list|None, skeleton_points list, source str).
        Errors: Không phát sinh; lỗi nội bộ fallback được nuốt và trả về None.
        """
        if weld_polygon and self._to_main_contour(weld_polygon) is not None:
            normalized_points = self._normalize_skeleton_points(weld_skeleton_points)
            source = (
                "weld_reference_or_shared_with_skeleton"
                if normalized_points
                else "shared_from_measurement_or_slit"
            )
            return weld_polygon, normalized_points, source

        if self.weld_seam_service is None:
            return None, [], "missing_runtime_polygon"

        try:
            polygons, center_points, _ = self.weld_seam_service.extract_weld_seam_reference(img)
            contour = self._to_main_contour(polygons)
            normalized_points = self._normalize_skeleton_points(center_points)
            if contour is None:
                return None, normalized_points, "fallback_failed"
            polygon_data = contour.reshape(-1, 2).tolist()
            return [polygon_data], normalized_points, "fallback_unet_skeleton"
        except Exception as error:
            print(f"⚠️ [WeldSeamAirBubbles] Fallback polygon runtime thất bại: {error}")
            return None, [], "fallback_failed"

    @staticmethod
    def _normalize_skeleton_points(points: Any) -> list[list[int]]:
        """Chuẩn hóa ``skeleton_points`` về list điểm ``[x, y]`` kiểu int.

        Input: ``points`` có thể là list/tuple/ndarray dạng Nx2 hoặc rỗng.
        Output: Danh sách điểm hợp lệ để vẽ và serialize JSON an toàn.
        Errors: Không phát sinh; phần tử không hợp lệ sẽ bị bỏ qua.
        """
        if points is None:
            return []
        normalized: list[list[int]] = []
        array = np.asarray(points, dtype=np.float32)
        if array.size == 0:
            return normalized
        try:
            reshaped = array.reshape(-1, 2)
        except ValueError:
            return normalized
        for x_raw, y_raw in reshaped:
            normalized.append([int(round(float(x_raw))), int(round(float(y_raw)))])
        return normalized



    def _xywh_to_xyxy(self, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        """Chuyển box dạng (x, y, width, height) sang (x1, y1, x2, y2).

        Input: box gồm bốn số nguyên.
        Output: tuple tọa độ hai góc đối diện.
        Errors: ``ValueError`` nếu box không có đúng bốn phần tử.
        """
        if not isinstance(box, (list, tuple)) or len(box) != 4:
            raise ValueError("bounding box phải có dạng (x, y, width, height)")
        x, y, w, h = box
        return x, y, x + w, y + h

    @staticmethod
    def _normalize_regions(regions: list) -> list[tuple[int, int, int, int]]:
        """Chuẩn hóa danh sách vùng về dạng ``(x, y, width, height)``.

        Input: Danh sách tuple/list xywh hoặc dict tọa độ xStart/yStart/xEnd/yEnd.
        Output: Danh sách vùng hợp lệ dạng tuple số nguyên.
        Errors: ``ValueError`` nếu vùng sai cấu trúc hoặc có kích thước không dương.
        """
        if not isinstance(regions, list):
            raise ValueError("Danh sách vùng kiểm tra phải là list")
        normalized = []
        for region in regions:
            if isinstance(region, Mapping):
                try:
                    x_start = int(region["xStart"])
                    y_start = int(region["yStart"])
                    x_end = int(region["xEnd"])
                    y_end = int(region["yEnd"])
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError("Vùng dict thiếu tọa độ") from error
                x, y = min(x_start, x_end), min(y_start, y_end)
                width, height = abs(x_end - x_start), abs(y_end - y_start)
            else:
                if not isinstance(region, (list, tuple)) or len(region) != 4:
                    raise ValueError("Vùng phải có dạng xywh hoặc dict tọa độ")
                x, y, width, height = (int(value) for value in region)
            if width <= 0 or height <= 0:
                raise ValueError("Kích thước vùng kiểm tra phải lớn hơn 0")
            normalized.append((x, y, width, height))
        return normalized
    
              

