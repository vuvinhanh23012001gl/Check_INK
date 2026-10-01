from typing import Any
import numpy as np
from .base_ai import JudgmentResult
from .border_detector import BorderDetector

class MeasurementWeldingDetector(BorderDetector):
	"""Đo chiều rộng đường hàn và phán định theo năm mức cấu hình."""

	INSPECTOR_NAME = "MeasurementWeldInspector"

	def define(
		self,
		image: np.ndarray,
		lines: list,
		Approx_value: float = 0.002,
		min_area: int = 100,
	) -> dict[str, Any]:
		"""Đo giao điểm chỉ trong phạm vi từng đoạn line cấu hình.

		Input: ảnh runtime, danh sách đoạn line và tham số lấy polygon UNet.
		Output: dict chứa polygon và kết quả 0/1/2 giao điểm từng đoạn.
		Errors: ``ValueError`` nếu ảnh hoặc danh sách line không hợp lệ.
		"""
		return super().define(image, lines, Approx_value, min_area)

	def compare(
		self,
		standard_data: dict,
		runtime_data: dict,
		scale_mm_per_pixel: float,
	) -> dict[str, Any]:
		"""So sánh chiều rộng runtime với level chuẩn của từng line.

		Input: ``standard_data`` theo cấu trúc ``MeasurementWeldInspector``;
			``runtime_data`` là output của ``define``; ``scale_mm_per_pixel``
			là hệ số calibration đổi pixel sang mm.
		Output: dict chứa polygon và kết quả phán định sơ bộ từng line.
		Errors: ``ValueError`` nếu chuẩn, runtime, level hoặc calibration
			không hợp lệ.
		"""
		if not isinstance(scale_mm_per_pixel, (int, float)) or scale_mm_per_pixel <= 0:
			raise ValueError("scale_mm_per_pixel phải là số lớn hơn 0")
		if not isinstance(standard_data, dict):
			raise ValueError("standard_data phải là dict MeasurementWeldInspector")
		if not isinstance(runtime_data, dict) or "lines" not in runtime_data:
			raise ValueError("runtime_data phải là output của define")
		standards = standard_data.get(self.INSPECTOR_NAME, standard_data)
		if not isinstance(standards, dict) or not standards:
			raise ValueError("MeasurementWeldInspector phải chứa ít nhất một line")
		runtime_by_index = {
			item["line_index"]: item for item in runtime_data["lines"]
		}
		comparisons = []
		for key, standard in standards.items():
			line_index = self._parse_line_index(key)
			levels = self._parse_levels(line_index, standard)
			runtime = runtime_by_index.get(line_index)
			intersection_count = (
				0 if runtime is None else int(runtime.get("intersection_count", 0))
			)
			distance_pixel = None if runtime is None else runtime.get("distance_pixel")
			distance_mm = (
				None
				if distance_pixel is None
				else float(distance_pixel) * float(scale_mm_per_pixel)
			)
			level, is_valid = self._classify_level(
				distance_mm,
				bool(
					runtime
					and runtime.get("is_valid")
					and intersection_count >= 2
				),
				levels,
			)
			comparisons.append({
				"line_index": line_index,
				"name_line": standard.get("name_line", str(line_index)),
				"standard_line": dict(standard),
				"runtime": runtime,
				"intersection_count": intersection_count,
				"distance_pixel": distance_pixel,
				"distance_mm": distance_mm,
				"scale_mm_per_pixel": float(scale_mm_per_pixel),
				"level": level,
				"is_valid": is_valid,
			})
		return {
			"comparisons": comparisons,
			"polygon": runtime_data.get("polygon"),
			"image": runtime_data.get("image"),
		}

	def judge(self, comparison_data: dict) -> JudgmentResult:
		"""Phán định toàn bộ line đo đường hàn thành OK hoặc NG.

		Input: dict output của ``compare``.
		Output: ``JudgmentResult``; chỉ OK khi mọi line thuộc level 4 hoặc 5.
		Errors: ``ValueError`` nếu thiếu danh sách comparison.
		"""
		if not isinstance(comparison_data, dict) or "comparisons" not in comparison_data:
			raise ValueError("comparison_data thiếu comparisons")
		comparisons = comparison_data["comparisons"]
		ok = bool(comparisons) and all(item["is_valid"] for item in comparisons)
		errors = []
		for item in comparisons:
			if not item["is_valid"]:
				standard = item["standard_line"]
				runtime = item.get("runtime")
				measured = bool(
					runtime
					and runtime.get("is_valid")
					and item["intersection_count"] >= 2
					and item["distance_mm"] is not None
				)
				actual = (
					f"{float(item['distance_mm']):g} mm"
					if measured
					else f"Không đo được ({item['intersection_count']} giao điểm)"
				)
				errors.append(
					f"[Khoảng cách đường hàn] NG - \"{item['name_line']}\" - "
					f"Quy định:\"{float(standard['level4']):g} mm - "
					f"{float(standard['level5']):g} mm\" - Thực tế :\"{actual}\""
				)
		return JudgmentResult(
			ok=ok,
			status="OK" if ok else "NG",
			standard_data={
				"inspector": self.INSPECTOR_NAME,
				"lines": [item["standard_line"] for item in comparisons],
			},
			runtime_data={
				"comparisons": comparisons,
				"image": comparison_data.get("image"),
			},
			comparison_data=comparison_data,
			message=(
				"Tất cả đường hàn đạt level 4 hoặc 5"
				if ok
				else "Có đường hàn nằm ngoài vùng OK (level 4-5)"
			),
			errors=errors,
		)

	@staticmethod
	def _parse_line_index(key: Any) -> int:
		"""Chuyển key line trong JSON thành số nguyên."""
		try:
			return int(key)
		except (TypeError, ValueError) as error:
			raise ValueError(f"ID line không hợp lệ: {key}") from error

	@staticmethod
	def _parse_levels(line_index: int, standard: dict) -> tuple[float, ...]:
		"""Đọc và kiểm tra năm level tăng dần của một line chuẩn."""
		if not isinstance(standard, dict):
			raise ValueError(f"Chuẩn line {line_index} phải là dict")
		try:
			levels = tuple(float(standard[f"level{index}"]) for index in range(1, 6))
		except (KeyError, TypeError, ValueError) as error:
			raise ValueError(f"Chuẩn line {line_index} thiếu level1..level5 hợp lệ") from error
		if any(left >= right for left, right in zip(levels, levels[1:])):
			raise ValueError(f"level1..level5 của line {line_index} phải tăng dần")
		return levels

	@staticmethod
	def _classify_level(
		distance_mm: float | None,
		runtime_is_valid: bool,
		levels: tuple[float, ...],
	) -> tuple[int | None, bool]:
		"""Xếp khoảng cách vào level theo ngưỡng trên bao gồm.

		Input: ``distance_mm`` là khoảng cách đo; ``runtime_is_valid`` cho biết
			line có đúng hai giao điểm; ``levels`` chứa ngưỡng trên level1..level5.
		Output: Cặp (level, is_ok); level 1-3 là NG, level 4-5 là OK, vượt
			level5 trả về (None, False).
		Errors: Không phát sinh; thiếu khoảng cách hoặc runtime không hợp lệ
			được trả về (None, False).
		"""
		if distance_mm is None or not runtime_is_valid:
			return None, False
		level1, level2, level3, level4, level5 = levels
		if distance_mm <= level1:
			return 1, False
		if distance_mm <= level2:
			return 2, False
		if distance_mm <= level3:
			return 3, False
		if distance_mm <= level4:
			return 4, True
		if distance_mm <= level5:
			return 5, True
		return None, False
