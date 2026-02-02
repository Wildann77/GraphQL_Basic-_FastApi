from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from src.core.logging import logger

if TYPE_CHECKING:
    from src.features.users.schemas import User


class BaseLoader:
    def __init__(self, session: AsyncSession):
        self.session = session


class UserLoader(BaseLoader):
    """Batch load users untuk hindari N+1 problem"""

    async def load_users(self, keys: List[int]) -> List[Optional["User"]]:
        from src.features.users.models import UserModel
        from src.features.users.schemas import User

        logger.info("dataloader_load_users", keys=keys)

        result = await self.session.execute(
            select(UserModel).where(UserModel.id.in_(keys))
        )

        users_map = {}
        for user in result.scalars().all():
            users_map[user.id] = User(
                id=user.id,  # type: ignore
                name=user.name,  # type: ignore
                email=user.email,  # type: ignore
                is_active=user.is_active,  # type: ignore
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

        return [users_map.get(key) for key in keys]

    def get_loader(self) -> DataLoader:
        return DataLoader(load_fn=self.load_users)


class Loaders:
    """Registry untuk semua dataloaders"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._user_loader: Optional[DataLoader] = None

    @property
    def user_loader(self) -> DataLoader:
        if self._user_loader is None:
            self._user_loader = UserLoader(self.session).get_loader()
        return self._user_loader
