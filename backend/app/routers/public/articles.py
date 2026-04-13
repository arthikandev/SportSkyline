"""
SportSkyline Backend — Public Router: Articles
GET /api/v1/articles/*
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleListOut, ArticleDetailOut
from app.schemas.system import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(prefix="/articles", tags=["Public – Articles"])


@router.get("", response_model=PaginatedResponse)
async def list_articles(
    sport: Optional[str] = Query(None, description="Sport slug filter"),
    category: Optional[str] = Query(None, description="Category slug filter"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    sport_id = None
    category_id = None

    if sport:
        from app.models.sport import Sport
        from sqlalchemy import select
        r = await db.execute(select(Sport).where(Sport.slug == sport))
        s = r.scalar_one_or_none()
        if s:
            sport_id = s.id

    if category:
        from app.models.article import ArticleCategory
        from sqlalchemy import select
        r = await db.execute(select(ArticleCategory).where(ArticleCategory.slug == category))
        c = r.scalar_one_or_none()
        if c:
            category_id = c.id

    offset = (page - 1) * limit
    items, total = await repo.get_published(sport_id=sport_id, category_id=category_id, offset=offset, limit=limit)
    out = [ArticleListOut.model_validate(a) for a in items]
    return paginate(out, total, page, limit)


@router.get("/featured", response_model=PaginatedResponse)
async def featured_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    offset = (page - 1) * limit
    items, total = await repo.get_published(is_featured=True, offset=offset, limit=limit)
    return paginate([ArticleListOut.model_validate(a) for a in items], total, page, limit)


@router.get("/trending", response_model=PaginatedResponse)
async def trending_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(8, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    offset = (page - 1) * limit
    items, total = await repo.get_published(is_trending=True, offset=offset, limit=limit)
    return paginate([ArticleListOut.model_validate(a) for a in items], total, page, limit)


@router.get("/breaking", response_model=PaginatedResponse)
async def breaking_news(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    items, total = await repo.get_published(is_breaking=True, limit=limit)
    return paginate([ArticleListOut.model_validate(a) for a in items], total, 1, limit)


@router.get("/by-category/{category_slug}", response_model=PaginatedResponse)
async def articles_by_category(
    category_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    from app.models.article import ArticleCategory
    from sqlalchemy import select
    r = await db.execute(select(ArticleCategory).where(ArticleCategory.slug == category_slug))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    repo = ArticleRepository(db)
    offset = (page - 1) * limit
    items, total = await repo.get_published(category_id=cat.id, offset=offset, limit=limit)
    return paginate([ArticleListOut.model_validate(a) for a in items], total, page, limit)


@router.get("/by-tag/{tag_slug}", response_model=list)
async def articles_by_tag(
    tag_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    offset = (page - 1) * limit
    items = await repo.get_by_tag_slug(tag_slug, offset=offset, limit=limit)
    return [ArticleListOut.model_validate(a) for a in items]


@router.get("/related/{slug}", response_model=list)
async def related_articles(
    slug: str,
    limit: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
):
    repo = ArticleRepository(db)
    article = await repo.get_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    items, _ = await repo.get_published(sport_id=article.sport_id, limit=limit + 1)
    related = [a for a in items if a.id != article.id][:limit]
    return [ArticleListOut.model_validate(a) for a in related]


@router.get("/{slug}", response_model=ArticleDetailOut)
async def article_detail(slug: str, db: AsyncSession = Depends(get_db)):
    repo = ArticleRepository(db)
    article = await repo.get_by_slug(slug)
    if not article or article.status != "published":
        raise HTTPException(status_code=404, detail="Article not found")
    await repo.increment_view(article.id)
    return ArticleDetailOut.model_validate(article)
