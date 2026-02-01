import strawberry
from typing import Optional, List


@strawberry.interface
class Error:
    """Base error interface"""
    message: str
    code: str


@strawberry.type
class NotFoundError(Error):
    """Resource tidak ditemukan"""
    code: str = "NOT_FOUND"


@strawberry.type
class ValidationError(Error):
    """Input validation error"""
    code: str = "VALIDATION_ERROR"
    field: Optional[str] = None


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


# Union types untuk GraphQL
from typing import Union

UserResult = Union["User", NotFoundError, ValidationError]
UsersResult = Union[List["User"], DatabaseError]
MutationResult = Union["User", ValidationError, NotFoundError]