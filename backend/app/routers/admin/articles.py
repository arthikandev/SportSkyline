"""
SportSkyline Backend — Admin Router: Articles CRUD
/api/v1/admin/articles/*
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleListOut, ArticleDetailOut, ScheduleRequest
from app.schemas.system import PaginatedResponse
from app.services.article_service import ArticleService
from app.utils.pagination import paginate

router = APIRouter(prefix="/admin/articles", tags=["Admin – Articles"])


@router.get("", response_model=PaginatedResponse)
async def list_all_articles(
    status: Optional[str] = Query(None),
    sport_id: Optional[uuid.UUID] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all articles including drafts (admin only)."""
    repo = ArticleRepository(db)
    filters = {}
    if status:
        filters["status"] = status
    if sport_id:
        filters["sport_id"] = sport_id
    offset = (page - 1) * limit
    items, total = await repo.get_all(filters=filters, offset=offset, limit=limit)
    return paginate([ArticleListOut.model_validate(a) for a in items], total, page, limit)


@router.post("", response_model=ArticleDetailOut, status_code=201)
async def create_article(
    payload: ArticleCreate,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.create(payload, admin_id=admin.id)
    return ArticleDetailOut.model_validate(article)


@router.get("/{article_id}", response_model=ArticleDetailOut)
async def get_article(
    article_id: uuid.UUID,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    article = await repo.get(article_id)
    if not article or article.deleted_at:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleDetailOut.model_validate(article)


@router.put("/{article_id}", response_model=ArticleDetailOut)
async def update_article(
    article_id: uuid.UUID,
    payload: ArticleUpdate,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.update(article_id, payload, admin_id=admin.id)
    return ArticleDetailOut.model_validate(article)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: uuid.UUID,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    await service.delete(article_id, admin_id=admin.id)


@router.post("/{article_id}/publish", response_model=ArticleDetailOut)
async def publish_article(
    article_id: uuid.UUID,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.publish(article_id, admin_id=admin.id)
    return ArticleDetailOut.model_validate(article)


@router.post("/{article_id}/schedule", response_model=ArticleDetailOut)
async def schedule_article(
    article_id: uuid.UUID,
    payload: ScheduleRequest,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.schedule(article_id, payload, admin_id=admin.id)
    return ArticleDetailOut.model_validate(article)


@router.post("/{article_id}/unpublish", response_model=ArticleDetailOut)
async def unpublish_article(
    article_id: uuid.UUID,
    admin: Admin = Depends(require_editor_or_above()),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    article = await service.unpublish(article_id, admin_id=admin.id)
    return ArticleDetailOut.model_validate(article)
