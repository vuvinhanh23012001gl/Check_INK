from typing import Any

from .base_ai import JudgmentResult
from .border_detector import BorderDetector


class SlitDetector(BorderDetector):
	"""Đo độ rộng khe hàn và phán định theo khoảng min/max."""

	INSPECTOR_NAME = "SlitWeldInspector"

	def compare(
		self,
		standard_data: dict,
		runtime_data: dict,
		scale_mm_per_pixel: float,
	) -> dict[str, Any]:
		"""So sánh độ rộng khe runtime với khoảng chuẩn từng line.

		Input: ``standard_data`` theo cấu trúc ``SlitWeldInspector``;
			``runtime_data`` là output của ``define``; ``scale_mm_per_pixel``
			là hệ số calibration đổi pixel sang mm.
		Output: dict chứa polygon và kết quả so sánh từng line.
		Errors: ``ValueError`` nếu chuẩn, runtime hoặc calibration không hợp lệ.
		"""
		if not isinstance(scale_mm_per_pixel, (int, float)) or scale_mm_per_pixel <= 0:
			raise ValueError("scale_mm_per_pixel phải là số lớn hơn 0")
		if not isinstance(standard_data, dict):
			raise ValueError("standard_data phải là dict SlitWeldInspector")
		if not isinstance(runtime_data, dict) or "lines" not in runtime_data:
			raise ValueError("runtime_data phải là output của define")
		standards = standard_data.get(self.INSPECTOR_NAME, standard_data)
		if not isinstance(standards, dict) or not standards:
			raise ValueError("SlitWeldInspector phải chứa ít nhất một line")

		runtime_by_index = {
			item["line_index"]: item for item in runtime_data["lines"]
		}
		comparisons = []
		for key, standard in standards.items():
			line_index = self._parse_line_index(key)
			width_min, width_max = self._parse_width_range(line_index, standard)
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
			is_valid = bool(
				runtime
				and runtime.get("is_valid")
				and intersection_count == 2
				and distance_mm is not None
				and width_min <= distance_mm <= width_max
			)
			comparisons.append({
				"line_index": line_index,
				"name_line": standard.get("nameLine") or standard.get("name_line") or str(line_index),
				"standard_line": dict(standard),
				"width_min": width_min,
				"width_max": width_max,
				"runtime": runtime,
				"intersection_count": intersection_count,
				"distance_pixel": distance_pixel,
				"distance_mm": distance_mm,
				"scale_mm_per_pixel": float(scale_mm_per_pixel),
				"is_valid": is_valid,
			})
		return {
			"comparisons": comparisons,
			"polygon": runtime_data.get("polygon"),
			"image": runtime_data.get("image"),
		}

	def judge(self, comparison_data: dict) -> JudgmentResult:
		"""Phán định toàn bộ line khe hàn thành OK hoặc NG.

		Input: dict output của ``compare``.
		Output: ``JudgmentResult``; OK khi tất cả line nằm trong min/max.
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
				measured = bool(
					runtime
					and runtime.get("is_valid")
					and item["intersection_count"] == 2
					and item["distance_mm"] is not None
				)
				actual = (
					f"{float(item['distance_mm']):g} mm"
					if measured
					else f"Không đo được ({item['intersection_count']} giao điểm)"
				)
				errors.append(
					f"[Khoảng cách khe hàn] NG - \"{item['name_line']}\" - "
					f"Quy định:\"{float(item['width_min']):g} mm - "
					f"{float(item['width_max']):g} mm\" - Thực tế :\"{actual}\""
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
				"Tất cả khe hàn nằm trong khoảng chuẩn"
				if ok
				else "Có khe hàn nằm ngoài khoảng chuẩn"
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
	def _parse_width_range(line_index: int, standard: dict) -> tuple[float, float]:
		"""Đọc và kiểm tra khoảng widthMin/widthMax của line chuẩn."""
		if not isinstance(standard, dict):
			raise ValueError(f"Chuẩn line {line_index} phải là dict")
		try:
			width_min = float(standard["widthMin"])
			width_max = float(standard["widthMax"])
		except (KeyError, TypeError, ValueError) as error:
			raise ValueError(
				f"Chuẩn line {line_index} thiếu widthMin/widthMax hợp lệ"
			) from error
		if width_min < 0 or width_min >= width_max:
			raise ValueError(
				f"Line {line_index} yêu cầu 0 <= widthMin < widthMax"
			)
		return width_min, width_max
