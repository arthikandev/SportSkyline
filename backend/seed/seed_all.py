"""
SportSkyline Backend — Seed Data Script
Populates the database with initial sports, leagues, teams, and articles.
"""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from app.database import get_db_context
from app.models.sport import Sport, League, Season, Venue
from app.models.team import Team
from app.models.article import NewsArticle, ArticleCategory, ArticleAuthor
from app.models.admin import Admin
from app.middleware.auth import hash_password

async def seed_data():
    async with get_db_context() as db:
        logger_name = "SeedScript"
        print(f"[{logger_name}] Starting seed process...")

        # 1. Ensure Admin exists (as fallback)
        res = await db.execute(select(Admin).limit(1))
        admin = res.scalar_one_or_none()
        if not admin:
            print(f"[{logger_name}] Creating super admin...")
            admin = Admin(
                email="admin@sportskyline.com",
                password_hash=hash_password("Admin@123!"),
                full_name="Super Admin"
            )
            db.add(admin)
            await db.flush()

        # 2. Author
        res = await db.execute(select(ArticleAuthor).limit(1))
        author = res.scalar_one_or_none()
        if not author:
            print(f"[{logger_name}] Creating author...")
            author = ArticleAuthor(
                display_name="SportSkyline Editorial",
                admin_id=admin.id,
                bio="Official editorial team for SportSkyline."
            )
            db.add(author)
            await db.flush()

        # 3. Sports
        sports_data = [
            {"name": "Football", "slug": "football", "emoji": "⚽", "sort_order": 1},
            {"name": "Cricket", "slug": "cricket", "emoji": "🏏", "sort_order": 2},
            {"name": "Basketball", "slug": "basketball", "emoji": "🏀", "sort_order": 3},
            {"name": "Tennis", "slug": "tennis", "emoji": "🎾", "sort_order": 4},
            {"name": "Formula 1", "slug": "f1", "emoji": "🏎️", "sort_order": 5},
            {"name": "American Football", "slug": "nfl", "emoji": "🏈", "sort_order": 6},
        ]
        
        sports_map = {}
        for s_data in sports_data:
            res = await db.execute(select(Sport).where(Sport.slug == s_data["slug"]))
            sport = res.scalar_one_or_none()
            if not sport:
                sport = Sport(**s_data)
                db.add(sport)
                await db.flush()
            sports_map[s_data["slug"]] = sport

        # 4. Categories
        categories_data = [
            {"name": "Transfer News", "slug": "transfers", "sport_slug": "football"},
            {"name": "Match Previews", "slug": "previews", "sport_slug": "football"},
            {"name": "Live Analysis", "slug": "analysis", "sport_slug": "football"},
            {"name": "IPL Highlights", "slug": "ipl", "sport_slug": "cricket"},
        ]
        
        cat_map = {}
        for c_data in categories_data:
            res = await db.execute(select(ArticleCategory).where(ArticleCategory.slug == c_data["slug"]))
            cat = res.scalar_one_or_none()
            if not cat:
                sport = sports_map.get(c_data["sport_slug"])
                cat = ArticleCategory(
                    name=c_data["name"],
                    slug=c_data["slug"],
                    sport_id=sport.id if sport else None
                )
                db.add(cat)
                await db.flush()
            cat_map[c_data["slug"]] = cat

        # 5. Articles (Sample)
        articles_data = [
            {
                "title": "Mbappe Signs for Real Madrid on a 5-Year Deal",
                "slug": "mbappe-real-madrid-exclusive",
                "excerpt": "The French superstar finally completes his dream move to the Bernabéu.",
                "content": "Full story content goes here...",
                "status": "published",
                "is_featured": True,
                "is_hero": True,
                "sport_slug": "football",
                "cat_slug": "transfers"
            },
            {
                "title": "IPL 2026: Virat Kohli Smashes Century vs Mumbai Indians",
                "slug": "kohli-century-mi-ipl-2026",
                "excerpt": "A masterclass from the King as RCB registers a massive win.",
                "content": "Full story content goes here...",
                "status": "published",
                "is_featured": True,
                "is_trending": True,
                "sport_slug": "cricket",
                "cat_slug": "ipl"
            }
        ]

        for a_data in articles_data:
            res = await db.execute(select(NewsArticle).where(NewsArticle.slug == a_data["slug"]))
            if not res.scalar_one_or_none():
                sport = sports_map.get(a_data.pop("sport_slug"))
                cat = cat_map.get(a_data.pop("cat_slug"))
                article = NewsArticle(
                    **a_data,
                    sport_id=sport.id if sport else None,
                    category_id=cat.id if cat else None,
                    author_id=author.id,
                    published_at=datetime.now(timezone.utc)
                )
                db.add(article)
        
        await db.commit()
        print(f"[{logger_name}] Seeding completed successfully.")

if __name__ == "__main__":
    import sys
    import os
    # Add parent dir to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    asyncio.run(seed_data())
