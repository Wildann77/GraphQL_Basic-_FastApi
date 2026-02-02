from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

if TYPE_CHECKING:
    from src.features.users.schemas import User


class BaseLoader:
    def __init__(self, session: AsyncSession):
        self.session = session


class UserLoader(BaseLoader):
    """Batch load users untuk hindari N+1 problem"""

    async def load_users(self, keys: List[int]) -> List[Optional["User"]]:
        from src.core.logging import logger
        from src.features.users.repository import UserRepository
        from src.features.users.schemas import User

        logger.debug(
            "dataloader_batch_processing", loader="UserLoader", batch_size=len(keys)
        )

        repo = UserRepository(self.session)
        users_map = await repo.get_by_ids(keys)

        return [
            User(
                id=user.id,  # type: ignore
                name=user.name,  # type: ignore
                email=user.email,  # type: ignore
                is_active=user.is_active,  # type: ignore
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            if (user := users_map.get(key))
            else None
            for key in keys
        ]

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
