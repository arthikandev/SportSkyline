"""
SportSkyline Backend — Article Service
Business logic for article CRUD, publishing, scheduling, trending.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import NewsArticle, ArticleTag, ArticleCategory, ArticleAuthor
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleCreate, ArticleUpdate, ScheduleRequest
from app.utils.slug import unique_slug
from app.utils.audit import write_audit


class ArticleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ArticleRepository(db)

    async def create(
        self,
        payload: ArticleCreate,
        admin_id: Optional[uuid.UUID] = None,
    ) -> NewsArticle:
        # Generate unique slug
        slug = await unique_slug(
            payload.title,
            exists_fn=self.repo.slug_exists,
        )

        tag_ids = payload.tag_ids or []
        data = payload.model_dump(exclude={"tag_ids"})
        data["slug"] = slug

        article = await self.repo.create(data)

        # Attach tags
        if tag_ids:
            await self._set_tags(article, tag_ids)

        await write_audit(
            self.db,
            admin_id=admin_id,
            action="article.create",
            resource="news_articles",
            resource_id=article.id,
            new_data={"title": article.title, "slug": slug},
        )
        return article

    async def update(
        self,
        article_id: uuid.UUID,
        payload: ArticleUpdate,
        admin_id: Optional[uuid.UUID] = None,
    ) -> NewsArticle:
        article = await self.repo.get(article_id)
        if not article or article.deleted_at:
            raise HTTPException(status_code=404, detail="Article not found")

        old_data = {"title": article.title, "status": article.status}
        data = payload.model_dump(exclude_none=True, exclude={"tag_ids"})

        # Re-slug if title changed
        if "title" in data and data["title"] != article.title:
            data["slug"] = await unique_slug(data["title"], self.repo.slug_exists)

        updated = await self.repo.update(article_id, data)

        if payload.tag_ids is not None:
            await self._set_tags(updated, payload.tag_ids)

        await write_audit(
            self.db, admin_id=admin_id, action="article.update",
            resource="news_articles", resource_id=article_id,
            old_data=old_data, new_data=data,
        )
        return updated

    async def publish(self, article_id: uuid.UUID, admin_id: Optional[uuid.UUID] = None) -> NewsArticle:
        article = await self.repo.get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        article.status = "published"
        article.published_at = datetime.now(timezone.utc)
        article.scheduled_at = None
        await self.db.flush()
        await write_audit(self.db, admin_id, "article.publish", "news_articles", article_id)
        return article

    async def schedule(
        self, article_id: uuid.UUID, payload: ScheduleRequest,
        admin_id: Optional[uuid.UUID] = None
    ) -> NewsArticle:
        article = await self.repo.get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        article.status = "scheduled"
        article.scheduled_at = payload.scheduled_at
        await self.db.flush()
        await write_audit(self.db, admin_id, "article.schedule", "news_articles", article_id)
        return article

    async def unpublish(self, article_id: uuid.UUID, admin_id: Optional[uuid.UUID] = None) -> NewsArticle:
        article = await self.repo.get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        article.status = "draft"
        article.published_at = None
        await self.db.flush()
        await write_audit(self.db, admin_id, "article.unpublish", "news_articles", article_id)
        return article

    async def delete(self, article_id: uuid.UUID, admin_id: Optional[uuid.UUID] = None) -> None:
        success = await self.repo.soft_delete(article_id)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
        await write_audit(self.db, admin_id, "article.delete", "news_articles", article_id)

    async def _set_tags(self, article: NewsArticle, tag_ids: List[uuid.UUID]) -> None:
        from sqlalchemy import select
        result = await self.db.execute(
            select(ArticleTag).where(ArticleTag.id.in_(tag_ids))
        )
        tags = result.scalars().all()
        article.tags = list(tags)
        await self.db.flush()
