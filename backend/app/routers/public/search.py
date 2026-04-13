"""
SportSkyline Backend — Public Router: Search
GET /api/v1/search
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleListOut

router = APIRouter(prefix="/search", tags=["Public – Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    type: str = Query("articles", description="Type filter: articles"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Full-text search across published articles.
    Uses PostgreSQL plainto_tsquery on title + excerpt.
    """
    repo = ArticleRepository(db)
    offset = (page - 1) * limit
    items = await repo.full_text_search(q, offset=offset, limit=limit)
    return {
        "query": q,
        "results": [ArticleListOut.model_validate(a) for a in items],
        "count": len(items),
        "page": page,
        "limit": limit,
    }
