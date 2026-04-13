"""
SportSkyline Backend — Public Router: Homepage
GET /api/v1/homepage
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.homepage_service import get_homepage_feed

router = APIRouter(prefix="/homepage", tags=["Public – Homepage"])


@router.get("")
async def homepage_feed(db: AsyncSession = Depends(get_db)):
    """
    Full homepage data feed.
    Returns hero slides, trending strip, latest articles, live matches, and sidebar ad.
    Consumed by sports-homepage.html via homepage-data.js.
    """
    return await get_homepage_feed(db)


@router.get("/hero")
async def hero_items(db: AsyncSession = Depends(get_db)):
    """Hero slider items only."""
    data = await get_homepage_feed(db)
    return {"items": data["hero"]}


@router.get("/trending-strip")
async def trending_strip(db: AsyncSession = Depends(get_db)):
    """Trending strip articles only."""
    data = await get_homepage_feed(db)
    return {"items": data["trending"]}
