from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import logger
from src.features.users.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, user_id: int, include_deleted: bool = False
    ) -> Optional[UserModel]:
        query = select(UserModel).where(UserModel.id == user_id)
        if not include_deleted:
            query = query.where(UserModel.is_deleted.is_(False))

        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            logger.debug("user_fetched_by_id", user_id=user_id)
        return user

    async def get_by_ids(self, user_ids: List[int]) -> dict[int, UserModel]:
        """Batch fetch untuk DataLoader"""
        if not user_ids:
            return {}

        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id.in_(user_ids))
            .where(UserModel.is_deleted.is_(False))
        )
        users = {user.id: user for user in result.scalars().all() if user.id is not None}
        logger.debug("users_batch_fetched", count=len(users), requested_ids=len(user_ids))
        return users

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email)
            .where(UserModel.is_deleted.is_(False))
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug("user_fetched_by_email", email=email)
        return user

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        users = list(result.scalars().all())
        logger.debug("users_all_fetched", count=len(users), skip=skip, limit=limit)
        return users

    async def create(self, name: str, email: str) -> UserModel:
        existing = await self.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already registered")

        user = UserModel(name=name, email=email)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        logger.info("user_created", user_id=user.id, email=email)
        return user

    async def update(self, user_id: int, **kwargs) -> Optional[UserModel]:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness kalau diupdate
        if "email" in kwargs and kwargs["email"] != user.email:
            existing = await self.get_by_email(kwargs["email"])
            if existing:
                raise ValueError("Email already in use")

        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = func.now()
        await self.session.flush()
        await self.session.refresh(user)
        logger.info("user_updated", user_id=user_id)
        return user

    async def soft_delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.soft_delete()
        await self.session.flush()
        logger.info("user_soft_deleted", user_id=user_id)
        return True

    async def hard_delete(self, user_id: int) -> bool:
        """Hanya untuk admin, permanent delete"""
        user = await self.get_by_id(user_id, include_deleted=True)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        logger.info("user_hard_deleted", user_id=user_id)
        return True
