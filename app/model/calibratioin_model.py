class Calibration:

    def __init__(
        self,
        reality_mm: float = 0.0,
        pixel_mean: float = 0.0,
        pixel_std: float = 0.0,
        cv: float = 0.0,
        scale_mm_per_pixel: float = 0.0,
        scale_error_mm_per_pixel: float = 0.0,
        confidence: float = 0.0,
        samples_used: int = 0,
        samples_raw: int = 0,
        mad: float = 0.0
    ):
        self._reality_mm = reality_mm
        self._pixel_mean = pixel_mean
        self._pixel_std = pixel_std
        self._cv = cv
        self._scale_mm_per_pixel = scale_mm_per_pixel
        self._scale_error_mm_per_pixel = scale_error_mm_per_pixel
        self._confidence = confidence
        self._samples_used = samples_used
        self._samples_raw = samples_raw
        self._mad = mad

    # =========================
    # PROPERTIES
    # =========================

    @property
    def reality_mm(self) -> float:
        return self._reality_mm

    @reality_mm.setter
    def reality_mm(self, value: float):
        self._reality_mm = value

    @property
    def pixel_mean(self) -> float:
        return self._pixel_mean

    @pixel_mean.setter
    def pixel_mean(self, value: float):
        self._pixel_mean = value

    @property
    def pixel_std(self) -> float:
        return self._pixel_std

    @pixel_std.setter
    def pixel_std(self, value: float):
        self._pixel_std = value

    @property
    def cv(self) -> float:
        return self._cv

    @cv.setter
    def cv(self, value: float):
        self._cv = value

    @property
    def scale_mm_per_pixel(self) -> float:
        return self._scale_mm_per_pixel

    @scale_mm_per_pixel.setter
    def scale_mm_per_pixel(self, value: float):
        self._scale_mm_per_pixel = value

    @property
    def scale_error_mm_per_pixel(self) -> float:
        return self._scale_error_mm_per_pixel

    @scale_error_mm_per_pixel.setter
    def scale_error_mm_per_pixel(self, value: float):
        self._scale_error_mm_per_pixel = value

    @property
    def confidence(self) -> float:
        return self._confidence

    @confidence.setter
    def confidence(self, value: float):
        self._confidence = value

    @property
    def samples_used(self) -> int:
        return self._samples_used

    @samples_used.setter
    def samples_used(self, value: int):
        self._samples_used = value

    @property
    def samples_raw(self) -> int:
        return self._samples_raw

    @samples_raw.setter
    def samples_raw(self, value: int):
        self._samples_raw = value

    @property
    def mad(self) -> float:
        return self._mad

    @mad.setter
    def mad(self, value: float):
        self._mad = value

    # =========================
    # CV %
    # =========================

    @property
    def cv_percent(self) -> float:
        if self._pixel_mean == 0:
            return 0.0
        return self._cv * 100

    # =========================
    # CONVERT FUNCTIONS
    # =========================

    def pixel_to_mm(self, pixel: float) -> float:
        return pixel * self._scale_mm_per_pixel

    def mm_to_pixel(self, mm: float) -> float:
        if self._scale_mm_per_pixel == 0:
            return 0.0
        return mm / self._scale_mm_per_pixel

    # =========================
    # SERIALIZATION
    # =========================

    def to_dict(self) -> dict:
        return {
            "reality_mm": self._reality_mm,
            "pixel_mean": self._pixel_mean,
            "pixel_std": self._pixel_std,
            "cv": self._cv,
            "scale_mm_per_pixel": self._scale_mm_per_pixel,
            "scale_error_mm_per_pixel": self._scale_error_mm_per_pixel,
            "confidence": self._confidence,
            "samples_used": self._samples_used,
            "samples_raw": self._samples_raw,
            "mad": self._mad
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            reality_mm=data.get("reality_mm", 0.0),
            pixel_mean=data.get("pixel_mean", 0.0),
            pixel_std=data.get("pixel_std", 0.0),
            cv=data.get("cv", 0.0),
            scale_mm_per_pixel=data.get("scale_mm_per_pixel", 0.0),
            scale_error_mm_per_pixel=data.get("scale_error_mm_per_pixel", 0.0),
            confidence=data.get("confidence", 0.0),
            samples_used=data.get("samples_used", 0),
            samples_raw=data.get("samples_raw", 0),
            mad=data.get("mad", 0.0)
        )