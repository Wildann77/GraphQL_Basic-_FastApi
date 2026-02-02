from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ValidationError
from src.core.logging import logger
from src.features.users.models import UserModel
from src.features.users.repository import UserRepository
from src.features.users.schemas import (
    CreateUserInputValidation,
    UpdateUserInputValidation,
)
from src.features.users.schemas import (
    User as UserSchema,
)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    def _to_schema(self, model: UserModel) -> UserSchema:
        assert model.id is not None
        assert model.name is not None
        assert model.email is not None
        assert model.is_active is not None
        return UserSchema(
            id=model.id,
            name=model.name,
            email=model.email,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        users = await self.repository.get_all(skip=skip, limit=limit)
        return [self._to_schema(u) for u in users]

    async def get_user(self, user_id: int) -> Optional[UserSchema]:
        user = await self.repository.get_by_id(user_id)
        return self._to_schema(user) if user else None

    async def create_user(self, data: CreateUserInputValidation) -> UserSchema:
        try:
            user = await self.repository.create(data.name, str(data.email))
            await self.session.commit()
            return self._to_schema(user)
        except ValueError as e:
            await self.session.rollback()
            raise ValidationError(message=str(e), field="email")
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("database_integrity_error", error=str(e))
            raise ValidationError(message="Database error", field=None)

    async def update_user(
        self, user_id: int, data: UpdateUserInputValidation
    ) -> Optional[UserSchema]:
        try:
            user = await self.repository.update(
                user_id, name=data.name, email=str(data.email) if data.email else None
            )
            if not user:
                return None

            await self.session.commit()
            return self._to_schema(user)
        except ValueError as e:
            await self.session.rollback()
            raise ValidationError(message=str(e), field="email")

    async def delete_user(self, user_id: int) -> bool:
        result = await self.repository.soft_delete(user_id)
        if result:
            await self.session.commit()
        return result
