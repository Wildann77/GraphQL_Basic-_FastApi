import strawberry
from strawberry.types import Info

from src.core.exceptions import DatabaseError, ValidationError
from src.core.logging import logger
from src.features.users.schemas import (
    CreateUserInput,
    DeleteResponse,
    UpdateUserInput,
    UserCollection,
    UserMutationSuccess,
    UserNotFoundError,
    UserResponse,
    UsersResponse,
)
from src.features.users.service import UserService


@strawberry.type
class UserQuery:
    @strawberry.field
    async def users(self, info: Info, skip: int = 0, limit: int = 100) -> UsersResponse:
        logger.info("query_users", skip=skip, limit=limit)
        try:
            session = info.context["session"]
            service = UserService(session)
            items = await service.list_users(skip, limit)
            return UserCollection(items=items)
        except Exception as e:
            logger.error("query_users_error", error=str(e))
            return DatabaseError(message="Failed to fetch users", code="DB_ERROR")

    @strawberry.field
    async def user(self, info: Info, id: int) -> UserResponse:
        logger.info("query_user", user_id=id)
        try:
            # Menggunakan DataLoader untuk mendukung concurrency/batch query
            loaders = info.context["loaders"]
            result = await loaders.user_loader.load(id)

            if not result:
                return UserNotFoundError()

            return result
        except Exception as e:
            logger.error("query_user_error", error=str(e), user_id=id)
            return DatabaseError(message="Failed to fetch user", code="DB_ERROR")


@strawberry.type
class UserMutation:
    @strawberry.mutation
    async def createUser(self, info: Info, input: CreateUserInput) -> UserResponse:
        session = info.context["session"]
        service = UserService(session)

        try:
            validated = input.validate()
            return await service.create_user(validated)
        except ValidationError as e:
            return e
        except Exception as e:
            logger.error("create_user_error", error=str(e))
            return ValidationError(message="Internal error", field=None)

    @strawberry.mutation
    async def updateUser(
        self, info: Info, id: int, input: UpdateUserInput
    ) -> UserResponse:
        session = info.context["session"]
        service = UserService(session)

        try:
            validated = input.validate()
            result = await service.update_user(id, validated)

            if not result:
                return UserNotFoundError()

            return result
        except ValidationError as e:
            return e

    @strawberry.mutation
    async def deleteUser(self, info: Info, id: int) -> DeleteResponse:
        session = info.context["session"]
        service = UserService(session)

        result = await service.delete_user(id)
        if not result:
            return UserNotFoundError()

        return UserMutationSuccess(success=True, message="User deleted successfully")
