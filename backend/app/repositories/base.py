"""
SportSkyline Backend — Base Repository
Generic async CRUD operations for SQLAlchemy models.
"""
from __future__ import annotations
import uuid
from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        offset: int = 0,
        limit: int = 20,
        order_by=None,
    ) -> tuple[Sequence[ModelType], int]:
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        if filters:
            for attr, value in filters.items():
                col = getattr(self.model, attr, None)
                if col is not None and value is not None:
                    stmt = stmt.where(col == value)
                    count_stmt = count_stmt.where(col == value)

        # Soft-delete filter
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
            count_stmt = count_stmt.where(self.model.deleted_at.is_(None))

        if order_by is not None:
            stmt = stmt.order_by(order_by)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def create(self, data: Dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: uuid.UUID, data: Dict[str, Any]) -> Optional[ModelType]:
        obj = await self.get(id)
        if not obj:
            return None
        for key, value in data.items():
            if hasattr(obj, key) and value is not None:
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def soft_delete(self, id: uuid.UUID) -> bool:
        from datetime import datetime, timezone
        obj = await self.get(id)
        if not obj:
            return False
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(timezone.utc)
        else:
            await self.db.delete(obj)
        await self.db.flush()
        return True

    async def hard_delete(self, id: uuid.UUID) -> bool:
        obj = await self.get(id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.flush()
        return True

    async def exists(self, **kwargs) -> bool:
        stmt = select(func.count()).select_from(self.model)
        for attr, value in kwargs.items():
            col = getattr(self.model, attr, None)
            if col is not None:
                stmt = stmt.where(col == value)
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
