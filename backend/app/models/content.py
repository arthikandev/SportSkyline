"""
SportSkyline Backend — ORM Models: Featured Sections, Homepage Blocks
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class FeaturedSection(Base):
    __tablename__ = "featured_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    max_items = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    blocks = relationship("HomepageBlock", back_populates="section", cascade="all, delete-orphan")


class HomepageBlock(Base):
    __tablename__ = "homepage_blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("featured_sections.id"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("news_articles.id"), nullable=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=True)
    block_type = Column(String(50), default="article")
    # article | match | ad | custom
    sort_order = Column(Integer, default=0)
    custom_title = Column(Text)
    custom_subtitle = Column(Text)
    is_active = Column(Boolean, default=True)
    valid_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section = relationship("FeaturedSection", back_populates="blocks")
    article = relationship("NewsArticle", back_populates="homepage_blocks")
    match = relationship("Match", back_populates="homepage_blocks")
