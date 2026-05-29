from .erro_code import ERROR_MESSAGE
class Result:
    def __init__(self, ok: bool, data=None, error=None):
        self.ok = ok
        self.data = data
        self.error = error

    @staticmethod
    def Ok(data=None):
        return Result(True, data=data)

    @staticmethod
    def Fail(error):
        return Result(False, error=error)

    def message(self):
        if self.error is None:
            return None
        return ERROR_MESSAGE.get(self.error, "Unknown error")

    def __repr__(self):
        if self.ok:
            return f"<Result OK data={type(self.data)}>"
        return f"<Result FAIL error={self.error}>"
    
    def to_dict(self):
        return {
            "ok": self.ok,
            "data": self.data,
            "error_code": self.error.value if self.error else None,
            "error_name": self.error.name if self.error else None,
            "message": self.message()
        }