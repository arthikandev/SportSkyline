"""
SportSkyline Backend — Homepage Service
Assembles the homepage feed from multiple data sources.
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.article import NewsArticle
from app.models.match import Match
from app.models.ad import Banner
from datetime import datetime, timezone


async def get_homepage_feed(db: AsyncSession) -> dict:
    """
    Aggregates all data needed for sports-homepage.html.
    Returns a structured dict that the frontend JS can consume.
    """
    now = datetime.now(timezone.utc)

    # Hero slider (is_hero + published)
    hero_result = await db.execute(
        select(NewsArticle)
        .options(selectinload(NewsArticle.sport), selectinload(NewsArticle.category))
        .where(
            NewsArticle.is_hero.is_(True),
            NewsArticle.status == "published",
            NewsArticle.deleted_at.is_(None),
        )
        .order_by(desc(NewsArticle.published_at))
        .limit(5)
    )
    hero_articles = hero_result.scalars().all()

    # Trending strip
    trending_result = await db.execute(
        select(NewsArticle)
        .options(selectinload(NewsArticle.sport))
        .where(
            NewsArticle.is_trending.is_(True),
            NewsArticle.status == "published",
            NewsArticle.deleted_at.is_(None),
        )
        .order_by(desc(NewsArticle.trending_score))
        .limit(8)
    )
    trending = trending_result.scalars().all()

    # Latest articles
    latest_result = await db.execute(
        select(NewsArticle)
        .options(selectinload(NewsArticle.category), selectinload(NewsArticle.author))
        .where(NewsArticle.status == "published", NewsArticle.deleted_at.is_(None))
        .order_by(desc(NewsArticle.published_at))
        .limit(6)
    )
    latest = latest_result.scalars().all()

    # Live matches
    live_result = await db.execute(
        select(Match)
        .options(selectinload(Match.home_team), selectinload(Match.away_team),
                 selectinload(Match.sport), selectinload(Match.league))
        .where(Match.status.in_(["live", "half_time"]))
        .order_by(Match.scheduled_at)
        .limit(10)
    )
    live_matches = live_result.scalars().all()

    # Sidebar ad
    ad_result = await db.execute(
        select(Banner)
        .where(
            Banner.placement == "sidebar_top",
            Banner.is_active.is_(True),
            (Banner.start_date.is_(None)) | (Banner.start_date <= now),
            (Banner.end_date.is_(None)) | (Banner.end_date >= now),
        )
        .order_by(Banner.created_at.desc())
        .limit(1)
    )
    sidebar_ad = ad_result.scalar_one_or_none()

    def article_to_dict(a: NewsArticle) -> dict:
        return {
            "id": str(a.id),
            "title": a.title,
            "slug": a.slug,
            "excerpt": a.excerpt,
            "featured_image_url": a.featured_image_url,
            "category": a.category.name if a.category else None,
            "category_slug": a.category.slug if a.category else None,
            "sport": a.sport.name if a.sport else None,
            "sport_emoji": a.sport.emoji if a.sport else None,
            "author": a.author.display_name if a.author else "SportSkyline Editorial",
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "read_time_minutes": a.read_time_minutes,
            "is_breaking": a.is_breaking,
            "is_featured": a.is_featured,
        }

    def match_to_dict(m: Match) -> dict:
        return {
            "id": str(m.id),
            "sport": m.sport.name if m.sport else None,
            "sport_emoji": m.sport.emoji if m.sport else None,
            "league": m.league.name if m.league else None,
            "round": m.round,
            "status": m.status,
            "match_time": m.match_time,
            "home_team": m.home_team.name if m.home_team else None,
            "away_team": m.away_team.name if m.away_team else None,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "home_score_detail": m.home_score_detail,
            "away_score_detail": m.away_score_detail,
        }

    return {
        "hero": [article_to_dict(a) for a in hero_articles],
        "trending": [article_to_dict(a) for a in trending],
        "latest": [article_to_dict(a) for a in latest],
        "live_matches": [match_to_dict(m) for m in live_matches],
        "sidebar_ad": {
            "image_url": sidebar_ad.image_url,
            "link_url": sidebar_ad.link_url,
            "name": sidebar_ad.name,
        } if sidebar_ad else None,
    }
