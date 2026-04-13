"""
SportSkyline Backend — Background Jobs
Handles scheduled tasks like trending recomputation and publishing.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.database import AsyncSessionLocal
from app.models.article import NewsArticle

scheduler = AsyncIOScheduler()

async def recompute_trending_scores():
    """
    Background job to update trending scores for articles.
    Score = (Views in last 24h) / (Hours since published + 2)^1.5
    For now, we'll use a simplified version based on view_count and age.
    """
    logger.info("Computing trending scores...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(NewsArticle).where(
                NewsArticle.status == "published",
                NewsArticle.deleted_at.is_(None)
            )
        )
        articles = result.scalars().all()
        now = datetime.now(timezone.utc)
        
        for article in articles:
            if not article.published_at:
                continue
            
            hours_age = (now - article.published_at).total_seconds() / 3600
            score = article.view_count / ((hours_age + 2) ** 1.5)
            
            article.trending_score = score
            article.is_trending = score > 10.0 # Arbitrary threshold
            
        await db.commit()
    logger.info("Trending score computation complete.")

def start_scheduler():
    scheduler.add_job(recompute_trending_scores, "interval", minutes=15)
    scheduler.start()
    logger.info("Background scheduler started.")
