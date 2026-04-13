"""
SportSkyline Backend — Models Package
Import all models here so Alembic can detect them.
"""
from app.models.admin import Admin, Role, Permission
from app.models.sport import Sport, League, Season, Venue
from app.models.team import Team, Player
from app.models.match import Match, LiveScore, MatchEvent, MatchStatistic
from app.models.standing import Standing
from app.models.article import NewsArticle, ArticleCategory, ArticleTag, ArticleAuthor, article_tag_map
from app.models.content import FeaturedSection, HomepageBlock
from app.models.ad import Banner, Advertisement, MediaAsset
from app.models.system import AppSetting, AuditLog, Notification

__all__ = [
    "Admin", "Role", "Permission",
    "Sport", "League", "Season", "Venue",
    "Team", "Player",
    "Match", "LiveScore", "MatchEvent", "MatchStatistic",
    "Standing",
    "NewsArticle", "ArticleCategory", "ArticleTag", "ArticleAuthor", "article_tag_map",
    "FeaturedSection", "HomepageBlock",
    "Banner", "Advertisement", "MediaAsset",
    "AppSetting", "AuditLog", "Notification",
]
