from datetime import datetime
from typing import List, Optional, Union

import strawberry
from pydantic import BaseModel, EmailStr, Field

from src.core.exceptions import DatabaseError, ValidationError


# Pydantic untuk validation
class CreateUserInputValidation(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

    class Config:
        frozen = True


class UpdateUserInputValidation(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


# Strawberry types
@strawberry.type
class User:
    id: int
    name: str
    email: str
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@strawberry.type
class UserCollection:
    items: List[User]


# Extra Response Types
@strawberry.type
class UserExistsError:
    message: str = "User with this email already exists"
    code: str = "USER_EXISTS"


@strawberry.type
class UserNotFoundError:
    message: str = "User not found"
    code: str = "USER_NOT_FOUND"


@strawberry.type
class UserMutationSuccess:
    success: bool
    message: str


# Union types for GraphQL Responses

UserResponse = Union[User, UserNotFoundError, ValidationError, DatabaseError]
UsersResponse = Union[UserCollection, DatabaseError]
DeleteResponse = Union[UserMutationSuccess, UserNotFoundError]


@strawberry.input
class CreateUserInput:
    name: str
    email: str

    def validate(self) -> CreateUserInputValidation:
        return CreateUserInputValidation(name=self.name, email=self.email)


@strawberry.input
class UpdateUserInput:
    name: Optional[str] = None
    email: Optional[str] = None

    def validate(self) -> UpdateUserInputValidation:
        return UpdateUserInputValidation(name=self.name, email=self.email)
