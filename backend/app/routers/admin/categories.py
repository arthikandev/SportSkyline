"""
SportSkyline Backend — Admin Router: Article Categories & Tags
/api/v1/admin/categories/*
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.models.article import ArticleCategory, ArticleTag
from app.schemas.article import CategoryCreate, CategoryUpdate, CategoryOut, TagCreate, TagOut
from app.utils.slug import unique_slug

router = APIRouter(prefix="/admin", tags=["Admin – Categories & Tags"])


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(select(ArticleCategory).order_by(ArticleCategory.sort_order))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    async def _slug_exists(s: str) -> bool:
        res = await db.execute(select(ArticleCategory).where(ArticleCategory.slug == s))
        return res.scalar_one_or_none() is not None

    slug = await unique_slug(payload.name, _slug_exists)
    cat = ArticleCategory(**payload.model_dump(), slug=slug)
    db.add(cat)
    await db.flush()
    return cat


@router.get("/tags", response_model=List[TagOut])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(select(ArticleTag).order_by(ArticleTag.name))
    return result.scalars().all()


@router.post("/tags", response_model=TagOut, status_code=201)
async def create_tag(
    payload: TagCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    async def _slug_exists(s: str) -> bool:
        res = await db.execute(select(ArticleTag).where(ArticleTag.slug == s))
        return res.scalar_one_or_none() is not None

    slug = await unique_slug(payload.name, _slug_exists)
    tag = ArticleTag(**payload.model_dump(), slug=slug)
    db.add(tag)
    await db.flush()
    return tag
