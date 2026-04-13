"""
SportSkyline Backend — ORM Models: Sports, Leagues, Seasons, Venues
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    emoji = Column(String(10))
    icon_url = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    leagues = relationship("League", back_populates="sport")
    teams = relationship("Team", back_populates="sport")
    matches = relationship("Match", back_populates="sport")
    articles = relationship("NewsArticle", back_populates="sport")
    categories = relationship("ArticleCategory", back_populates="sport")


class League(Base):
    __tablename__ = "leagues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    short_name = Column(String(50))
    logo_url = Column(Text)
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sport = relationship("Sport", back_populates="leagues")
    seasons = relationship("Season", back_populates="league")
    matches = relationship("Match", back_populates="league")


class Season(Base):
    __tablename__ = "seasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # '2025/26'
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    league = relationship("League", back_populates="seasons")
    matches = relationship("Match", back_populates="season")
    standings = relationship("Standing", back_populates="season")


class Venue(Base):
    __tablename__ = "venues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    capacity = Column(Integer)
    surface = Column(String(50))  # 'grass', 'artificial', 'clay'
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    matches = relationship("Match", back_populates="venue")
