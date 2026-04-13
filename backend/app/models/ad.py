"""
SportSkyline Backend — ORM Models: Banners, Advertisements, Media Assets
"""
import uuid
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    placement = Column(String(100), nullable=False, index=True)
    # sidebar_top | article_mid | homepage_leaderboard | article_top | footer
    image_url = Column(Text, nullable=False)
    link_url = Column(Text)
    target_blank = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    impression_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    advertisements = relationship("Advertisement", back_populates="banner")


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    banner_id = Column(UUID(as_uuid=True), ForeignKey("banners.id"), nullable=True)
    ad_type = Column(String(50), default="display")  # display | native | video
    title = Column(String(300))
    description = Column(Text)
    cta_text = Column(String(100))
    priority = Column(Integer, default=0)
    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    banner = relationship("Banner", back_populates="advertisements")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    filename = Column(String(500), nullable=False)
    original_name = Column(String(500))
    url = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    mime_type = Column(String(100))
    size_bytes = Column(BigInteger)
    width = Column(Integer)
    height = Column(Integer)
    alt_text = Column(Text)
    caption = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploaded_by_admin = relationship("Admin", back_populates="media_assets")
