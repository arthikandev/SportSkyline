"""
SportSkyline Backend — Public Router: Ads/Banners
GET /api/v1/ads/{placement}
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ad import Banner

router = APIRouter(prefix="/ads", tags=["Public – Ads"])


@router.get("/{placement}")
async def get_ad_for_placement(placement: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the active banner for a given placement slot.
    Placement values: sidebar_top | article_mid | homepage_leaderboard | footer
    Also increments the impression counter.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Banner)
        .where(
            Banner.placement == placement,
            Banner.is_active.is_(True),
            (Banner.start_date.is_(None)) | (Banner.start_date <= now),
            (Banner.end_date.is_(None)) | (Banner.end_date >= now),
        )
        .order_by(Banner.created_at.desc())
        .limit(1)
    )
    banner = result.scalar_one_or_none()
    if not banner:
        return {"ad": None}

    # Increment impression
    banner.impression_count = (banner.impression_count or 0) + 1
    await db.flush()

    return {
        "ad": {
            "id": str(banner.id),
            "placement": banner.placement,
            "image_url": banner.image_url,
            "link_url": banner.link_url,
            "target_blank": banner.target_blank,
            "name": banner.name,
        }
    }


@router.post("/{banner_id}/click")
async def record_click(banner_id: str, db: AsyncSession = Depends(get_db)):
    """Record a click on a banner."""
    import uuid as _uuid
    try:
        bid = _uuid.UUID(banner_id)
    except ValueError:
        return {"ok": False}
    result = await db.execute(select(Banner).where(Banner.id == bid))
    banner = result.scalar_one_or_none()
    if banner:
        banner.click_count = (banner.click_count or 0) + 1
        await db.flush()
    return {"ok": True}
