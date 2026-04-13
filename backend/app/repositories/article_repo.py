"""
SportSkyline Backend — Article Repository
Handles complex article queries (FTS, featured, trending, by sport, etc.)
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import func, or_, select, desc, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import NewsArticle, ArticleTag, article_tag_map
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[NewsArticle]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(NewsArticle, db)

    def _base_query(self):
        return (
            select(NewsArticle)
            .where(NewsArticle.deleted_at.is_(None))
            .options(
                selectinload(NewsArticle.category),
                selectinload(NewsArticle.author),
                selectinload(NewsArticle.tags),
                selectinload(NewsArticle.sport),
            )
        )

    async def get_published(
        self,
        sport_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        is_featured: Optional[bool] = None,
        is_trending: Optional[bool] = None,
        is_breaking: Optional[bool] = None,
        is_hero: Optional[bool] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[NewsArticle], int]:
        stmt = self._base_query().where(NewsArticle.status == "published")
        count_stmt = (
            select(func.count())
            .select_from(NewsArticle)
            .where(NewsArticle.status == "published", NewsArticle.deleted_at.is_(None))
        )

        if sport_id:
            stmt = stmt.where(NewsArticle.sport_id == sport_id)
            count_stmt = count_stmt.where(NewsArticle.sport_id == sport_id)
        if category_id:
            stmt = stmt.where(NewsArticle.category_id == category_id)
            count_stmt = count_stmt.where(NewsArticle.category_id == category_id)
        if is_featured is not None:
            stmt = stmt.where(NewsArticle.is_featured == is_featured)
            count_stmt = count_stmt.where(NewsArticle.is_featured == is_featured)
        if is_trending is not None:
            stmt = stmt.where(NewsArticle.is_trending == is_trending)
            count_stmt = count_stmt.where(NewsArticle.is_trending == is_trending)
        if is_breaking is not None:
            stmt = stmt.where(NewsArticle.is_breaking == is_breaking)
            count_stmt = count_stmt.where(NewsArticle.is_breaking == is_breaking)
        if is_hero is not None:
            stmt = stmt.where(NewsArticle.is_hero == is_hero)
            count_stmt = count_stmt.where(NewsArticle.is_hero == is_hero)

        stmt = stmt.order_by(desc(NewsArticle.published_at)).offset(offset).limit(limit)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()
        result = await self.db.execute(stmt)
        return result.scalars().all(), total

    async def get_by_slug(self, slug: str) -> Optional[NewsArticle]:
        result = await self.db.execute(
            self._base_query().where(NewsArticle.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_tag_slug(self, tag_slug: str, offset: int = 0, limit: int = 10):
        stmt = (
            self._base_query()
            .join(article_tag_map, NewsArticle.id == article_tag_map.c.article_id)
            .join(ArticleTag, ArticleTag.id == article_tag_map.c.tag_id)
            .where(
                ArticleTag.slug == tag_slug,
                NewsArticle.status == "published",
            )
            .order_by(desc(NewsArticle.published_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def full_text_search(
        self, query: str, offset: int = 0, limit: int = 10
    ) -> Sequence[NewsArticle]:
        tsquery = func.plainto_tsquery("english", query)
        tsvector = func.to_tsvector(
            "english",
            func.coalesce(NewsArticle.title, "")
            + " "
            + func.coalesce(NewsArticle.excerpt, "")
        )
        stmt = (
            self._base_query()
            .where(
                tsvector.op("@@")(tsquery),
                NewsArticle.status == "published",
            )
            .order_by(desc(NewsArticle.published_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def slug_exists(self, slug: str) -> bool:
        return await self.exists(slug=slug)

    async def increment_view(self, article_id: uuid.UUID) -> None:
        from sqlalchemy import update
        await self.db.execute(
            update(NewsArticle)
            .where(NewsArticle.id == article_id)
            .values(view_count=NewsArticle.view_count + 1)
        )

    async def get_due_scheduled(self) -> Sequence[NewsArticle]:
        """Get articles scheduled for publishing that are now due."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(NewsArticle).where(
                NewsArticle.status == "scheduled",
                NewsArticle.scheduled_at <= now,
                NewsArticle.deleted_at.is_(None),
            )
        )
        return result.scalars().all()
