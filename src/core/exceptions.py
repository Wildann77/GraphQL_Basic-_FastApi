from typing import Optional

import strawberry


@strawberry.interface
class Error(Exception):
    """Base error interface"""

    message: str
    code: str

    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


@strawberry.type
class NotFoundError(Error):
    """Resource tidak ditemukan"""

    code: str = "NOT_FOUND"


@strawberry.type
class ValidationError(Error):
    """Input validation error"""

    code: str = "VALIDATION_ERROR"
    field: Optional[str] = None

    def __init__(
        self, message: str, code: str = "VALIDATION_ERROR", field: Optional[str] = None
    ):
        super().__init__(message, code)
        self.field = field


@strawberry.type
class AuthenticationError(Error):
    """Auth error"""

    code: str = "UNAUTHORIZED"


@strawberry.type
class RateLimitError(Error):
    """Rate limit exceeded"""

    code: str = "RATE_LIMIT_EXCEEDED"
    retry_after: int


@strawberry.type
class DatabaseError(Error):
    """Database error"""

    code: str = "DATABASE_ERROR"
