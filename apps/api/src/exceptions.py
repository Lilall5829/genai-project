from typing import Optional, Any
class ErrorCode:
    INVALID_JSON = "INVALID_JSON"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TIMEOUT = "TIMEOUT"

class APIException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        field: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details
        super().__init__(message)

class InvalidInputError(APIException):
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(
            error_code=ErrorCode.INVALID_VALUE,
            message=message,
            status_code=422,
            field=field,
            details=details,
        )

class NotFoundError(APIException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            error_code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404,
        )


class InternalError(APIException):
    def __init__(self, message:str = "Internal server error", details: Optional[Any] = None):
        super().__init__(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=message,
            status_code=500,
            details=details,
        )