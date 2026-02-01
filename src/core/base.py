from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Boolean, DateTime, func

Base = declarative_base()

class SoftDeleteMixin:
    """Mixin untuk soft delete"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = func.now()