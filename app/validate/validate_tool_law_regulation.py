from typing import Any
from app.core import Result
from app.core import ErrorCode

class ValidateToolLawRegulation:
    @staticmethod
    def validate_levels(data: dict[str, Any]) -> Result:
        int_keys = ["product", "frame", "items"]
        result = {}
        for key in int_keys:
            if key not in data:
                return Result.Fail(ErrorCode.INVALID_INPUT)
            value = data[key]
            if isinstance(value, bool):
                return Result.Fail(ErrorCode.INVALID_INPUT)
            try:
                result[key] = int(value)
            except (TypeError, ValueError):
                return Result.Fail(ErrorCode.INVALID_INPUT)
        # Validate Level1 -> Level5
        level_keys = [
            "Level1_auto",
            "Level2_auto",
            "Level3_auto",
            "Level4_auto",
            "Level5_auto",
        ]
        levels = []
        for key in level_keys:
            if key not in data:
                return Result.Fail(ErrorCode.INVALID_INPUT)
            value = data[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return Result.Fail(ErrorCode.INVALID_INPUT)
            levels.append(float(value))
        for i in range(len(levels) - 1):
            if levels[i] >= levels[i + 1]:
                return Result.Fail(ErrorCode.INVALID_INPUT)
        result["levels"] = levels
        return Result.Ok(result)
    
    @staticmethod
    def validate_judment_item(data: dict) -> Result:
        required_fields = [
            "product_id",
            "frame_id",
            "items_id",
        ]
        for field in required_fields:
            if field not in data:
                return Result.Fail(f"Thiếu trường '{field}'")
        for field in required_fields:
            try:
                value = int(data[field])
            except (TypeError, ValueError):
                return Result.Fail(f"'{field}' phải là số nguyên")
            if value == -1:
                return Result.Fail(f"'{field}' không được bằng -1")
        return Result.Ok()