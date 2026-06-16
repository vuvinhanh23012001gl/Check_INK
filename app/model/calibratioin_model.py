class Calibration:
    CALCULATION_PARAMETER = "calculation_parameters"
    RESULT_PARAMETER      = "result_parameters"
    
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
        mad: float = 0.0,
        startX: int = 0,        # Đã sửa mặc định thành số nguyên 0
        startY: int = 0,        # Đã sửa mặc định thành số nguyên 0
        endX: int = 0,          # Đã sửa mặc định thành số nguyên 0
        endY: int = 0,          # Đã sửa mặc định thành số nguyên 0
        id_tems: str = "",
        name_item: str = "",
        number_capture: int = 0
    ):
        # Thông tin calibration
        self._reality_mm = float(reality_mm)
        self._pixel_mean = float(pixel_mean)
        self._pixel_std = float(pixel_std)
        self._cv = float(cv)
        self._scale_mm_per_pixel = float(scale_mm_per_pixel)
        self._scale_error_mm_per_pixel = float(scale_error_mm_per_pixel)
        self._confidence = float(confidence)
        self._samples_used = int(samples_used)
        self._samples_raw = int(samples_raw)
        self._mad = float(mad)
        
        # Thông tin vị trí (Ép kiểu int toàn bộ)
        self._startX = int(startX)
        self._startY = int(startY)
        self._endX = int(endX)
        self._endY = int(endY)

        # Thông tin item
        self._id_tems = str(id_tems)
        self._name_item = str(name_item)
        self._number_capture = int(number_capture)

    # =========================
    # PROPERTIES (GỐC)
    # =========================

    @property
    def reality_mm(self) -> float:
        return self._reality_mm

    @reality_mm.setter
    def reality_mm(self, value: float):
        self._reality_mm = float(value)

    @property
    def pixel_mean(self) -> float:
        return self._pixel_mean

    @pixel_mean.setter
    def pixel_mean(self, value: float):
        self._pixel_mean = float(value)

    @property
    def pixel_std(self) -> float:
        return self._pixel_std

    @pixel_std.setter
    def pixel_std(self, value: float):
        self._pixel_std = float(value)

    @property
    def cv(self) -> float:
        return self._cv

    @cv.setter
    def cv(self, value: float):
        self._cv = float(value)

    @property
    def scale_mm_per_pixel(self) -> float:
        return self._scale_mm_per_pixel

    @scale_mm_per_pixel.setter
    def scale_mm_per_pixel(self, value: float):
        self._scale_mm_per_pixel = float(value)

    @property
    def scale_error_mm_per_pixel(self) -> float:
        return self._scale_error_mm_per_pixel

    @scale_error_mm_per_pixel.setter
    def scale_error_mm_per_pixel(self, value: float):
        self._scale_error_mm_per_pixel = float(value)

    @property
    def confidence(self) -> float:
        return self._confidence

    @confidence.setter
    def confidence(self, value: float):
        self._confidence = float(value)

    @property
    def samples_used(self) -> int:
        return self._samples_used

    @samples_used.setter
    def samples_used(self, value: int):
        self._samples_used = int(value)

    @property
    def samples_raw(self) -> int:
        return self._samples_raw

    @samples_raw.setter
    def samples_raw(self, value: int):
        self._samples_raw = int(value)

    @property
    def mad(self) -> float:
        return self._mad

    @mad.setter
    def mad(self, value: float):
        self._mad = float(value)

    # =========================
    # PROPERTIES (VỊ TRÍ) -> Đã chuyển Type Hint và Setter về int
    # =========================

    @property
    def startX(self) -> int:
        return self._startX

    @startX.setter
    def startX(self, value: int):
        self._startX = int(value)

    @property
    def startY(self) -> int:
        return self._startY

    @startY.setter
    def startY(self, value: int):
        self._startY = int(value)

    @property
    def endX(self) -> int:
        return self._endX

    @endX.setter
    def endX(self, value: int):
        self._endX = int(value)

    @property
    def endY(self) -> int:
        return self._endY

    @endY.setter
    def endY(self, value: int):
        self._endY = int(value)

    # =========================
    # PROPERTIES (ITEM)
    # =========================

    @property
    def id_tems(self) -> str:
        return self._id_tems

    @id_tems.setter
    def id_tems(self, value: str):
        self._id_tems = str(value)

    @property
    def name_item(self) -> str:
        return self._name_item

    @name_item.setter
    def name_item(self, value: str):
        self._name_item = str(value)

    @property
    def number_capture(self) -> int:
        return self._number_capture

    @number_capture.setter
    def number_capture(self, value: int):
        self._number_capture = int(value)

    # =========================
    # CV %
    # =========================

    @property
    def cv_percent(self) -> float:
        return self._cv * 100.0

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
            f"{Calibration.CALCULATION_PARAMETER}": {
                "number_capture": self._number_capture,
                "name_item": self._name_item,
                "id_tems": self._id_tems,
                "startX": self._startX,
                "startY": self._startY,
                "endX": self._endX,
                "endY": self._endY,
                "reality_mm": self._reality_mm
            },
            f"{Calibration.RESULT_PARAMETER}": {
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
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Calibration":
        calc_params = data.get(cls.CALCULATION_PARAMETER, {})
        res_params = data.get(cls.RESULT_PARAMETER, {})
        return cls(
            reality_mm=calc_params.get("reality_mm", 0.0),
            pixel_mean=res_params.get("pixel_mean", 0.0),
            pixel_std=res_params.get("pixel_std", 0.0),
            cv=res_params.get("cv", 0.0),
            scale_mm_per_pixel=res_params.get("scale_mm_per_pixel", 0.0),
            scale_error_mm_per_pixel=res_params.get("scale_error_mm_per_pixel", 0.0),
            confidence=res_params.get("confidence", 0.0),
            samples_used=res_params.get("samples_used", 0),
            samples_raw=res_params.get("samples_raw", 0),
            mad=res_params.get("mad", 0.0),
            
            # Ép giá trị mặc định về số nguyên 0 khi đọc từ Json cấu hình
            startX=calc_params.get("startX", 0),
            startY=calc_params.get("startY", 0),
            endX=calc_params.get("endX", 0),
            endY=calc_params.get("endY", 0),
            id_tems=calc_params.get("id_tems", ""),
            name_item=calc_params.get("name_item", ""),
            number_capture=calc_params.get("number_capture", 0)
        )

    def __repr__(self):
        return (
            f"Calibration("
            f"reality_mm={self._reality_mm}, "
            f"pixel_mean={self._pixel_mean}, "
            f"scale_mm_per_pixel={self._scale_mm_per_pixel}, "
            f"id_tems='{self._id_tems}', "
            f"name_item='{self._name_item}', "
            f"startX={self._startX}, "
            f"startY={self._startY}, "
            f"number_capture={self._number_capture})"
        )

    def set_calculation_parameters(
        self, 
        *, 
        reality_mm: float = None,
        startX: int = None,
        startY: int = None,
        endX: int = None,
        endY: int = None,
        id_tems: str = None,
        name_item: str = None,
        number_capture: int = None
    ) -> None:
        """Cập nhật các tham số cấu hình bằng cách truyền tham số đặt tên trực tiếp."""
        if reality_mm is not None:
            self.reality_mm = reality_mm
        if startX is not None:
            self.startX = startX
        if startY is not None:
            self.startY = startY
        if endX is not None:
            self.endX = endX
        if endY is not None:
            self.endY = endY
        if id_tems is not None:
            self.id_tems = id_tems
        if name_item is not None:
            self.name_item = name_item
        if number_capture is not None:
            self.number_capture = number_capture

    def set_result_parameters(
            self,
            *,
            pixel_mean: float = None,
            pixel_std: float = None,
            cv: float = None,
            scale_mm_per_pixel: float = None,
            scale_error_mm_per_pixel: float = None,
            confidence: float = None,
            samples_used: int = None,
            samples_raw: int = None,
            mad: float = None
        ) -> None:
            """Cập nhật các tham số kết quả đo (Result) bằng cách truyền tham số đặt tên trực tiếp."""
            if pixel_mean is not None:
                self.pixel_mean = pixel_mean
            if pixel_std is not None:
                self.pixel_std = pixel_std
            if cv is not None:
                self.cv = cv
            if scale_mm_per_pixel is not None:
                self.scale_mm_per_pixel = scale_mm_per_pixel
            if scale_error_mm_per_pixel is not None:
                self.scale_error_mm_per_pixel = scale_error_mm_per_pixel
            if confidence is not None:
                self.confidence = confidence
            if samples_used is not None:
                self.samples_used = samples_used
            if samples_raw is not None:
                self.samples_raw = samples_raw
            if mad is not None:
                self.mad = mad