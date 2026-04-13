"""
SportSkyline Backend — ORM Models: Articles, Categories, Tags, Authors
"""
import uuid
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Table, Text, func
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


# ── Association Table ──────────────────────────────────────────────────────
article_tag_map = Table(
    "article_tag_map",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("news_articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",     UUID(as_uuid=True), ForeignKey("article_tags.id",  ondelete="CASCADE"), primary_key=True),
)


class ArticleCategory(Base):
    __tablename__ = "article_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sport = relationship("Sport", back_populates="categories")
    articles = relationship("NewsArticle", back_populates="category")


class ArticleTag(Base):
    __tablename__ = "article_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("NewsArticle", secondary=article_tag_map, back_populates="tags")


class ArticleAuthor(Base):
    __tablename__ = "article_authors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    display_name = Column(String(150), nullable=False)
    bio = Column(Text)
    avatar_url = Column(Text)
    twitter_handle = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship("Admin", back_populates="authored_articles")
    articles = relationship("NewsArticle", back_populates="author")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    excerpt = Column(Text)
    content = Column(Text, nullable=False)
    featured_image_url = Column(Text)
    image_credit = Column(String(255))

    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("article_categories.id"), nullable=True, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("article_authors.id"), nullable=True)

    # Publish workflow
    status = Column(String(30), default="draft", index=True)
    # draft | review | published | scheduled | archived

    # Feature flags
    is_featured = Column(Boolean, default=False, index=True)
    is_trending = Column(Boolean, default=False, index=True)
    is_breaking = Column(Boolean, default=False)
    is_hero = Column(Boolean, default=False)

    # Metrics
    trending_score = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    read_time_minutes = Column(Integer, default=5)

    # Scheduling
    published_at = Column(DateTime(timezone=True), index=True)
    scheduled_at = Column(DateTime(timezone=True))

    # SEO
    seo_title = Column(String(500))
    seo_description = Column(Text)
    seo_keywords = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))  # soft delete

    # Relationships
    sport = relationship("Sport", back_populates="articles")
    category = relationship("ArticleCategory", back_populates="articles")
    author = relationship("ArticleAuthor", back_populates="articles")
    tags = relationship("ArticleTag", secondary=article_tag_map, back_populates="articles")
    homepage_blocks = relationship("HomepageBlock", back_populates="article")
