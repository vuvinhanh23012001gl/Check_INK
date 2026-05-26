from app.core import Result,ErrorCode
class ValidateCaptureProduct:
    def validate_int(self, value, error_code):
        try:
            return Result.Ok(), int(value)
        except (TypeError, ValueError):
            return Result.Fail(error_code), None

    # def validate_capture_frame(self, product_id, frame_id, x, y, z):
    #     fields = [
    #         (product_id, ErrorCode.PRODUCT_ID_INVALID),
    #         (frame_id, ErrorCode.FRAME_ID_INVALID),
    #         (x, ErrorCode.POINT_X_INVALID),
    #         (y, ErrorCode.POINT_Y_INVALID),
    #         (z, ErrorCode.POINT_Z_INVALID),
    #     ]
    #     results = []
    #     for value, error in fields:
    #         result, value = self.validate_int(value, error)
    #         if not result.ok:
    #             return result
    #         results.append(value)
    #     product_id, frame_id, x, y, z = results
    #     return Result.Ok()