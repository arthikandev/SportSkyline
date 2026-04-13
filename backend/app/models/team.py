"""
SportSkyline Backend — ORM Models: Teams, Players
"""
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(50))
    slug = Column(String(200), unique=True, nullable=False, index=True)
    logo_url = Column(Text)
    country = Column(String(100))
    city = Column(String(100))
    founded_year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sport = relationship("Sport", back_populates="teams")
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    won_matches = relationship("Match", foreign_keys="Match.winner_team_id", back_populates="winner_team")
    standings = relationship("Standing", back_populates="team")


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    position = Column(String(100))
    nationality = Column(String(100))
    date_of_birth = Column(Date)
    jersey_number = Column(Integer)
    photo_url = Column(Text)
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    team = relationship("Team", back_populates="players")
    match_events = relationship("MatchEvent", back_populates="player")
