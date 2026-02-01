from strawberry.dataloader import DataLoader
from typing import List, Optional, Dict
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseLoader:
    def __init__(self, session: AsyncSession):
        self.session = session

class UserLoader(BaseLoader):
    """Batch load users untuk hindari N+1 problem"""
    
    async def load_users(self, keys: List[int]) -> List[Optional[dict]]:
        from src.features.users.models import UserModel
        
        # Batch query: SELECT * FROM users WHERE id IN (...)
        result = await self.session.execute(
            select(UserModel).where(UserModel.id.in_(keys))
        )
        
        # Mapping id -> user
        users_map: Dict[int, UserModel] = {
            user.id: user for user in result.scalars().all()
        }
        
        # Return dalam urutan keys (DataLoader requirement)
        return [users_map.get(key) for key in keys]
    
    def get_loader(self) -> DataLoader:
        return DataLoader(load_fn=self.load_users)


class Loaders:
    """Registry untuk semua dataloaders"""
    def __init__(self, session: AsyncSession):
        self.session = session
        self._user_loader = None
    
    @property
    def user_loader(self) -> DataLoader:
        if self._user_loader is None:
            self._user_loader = UserLoader(self.session).get_loader()
        return self._user_loader