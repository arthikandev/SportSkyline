"""
SportSkyline Backend — ORM Models: Matches, LiveScores, MatchEvents, MatchStatistics
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sport_id = Column(UUID(as_uuid=True), ForeignKey("sports.id"), nullable=False, index=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=True, index=True)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id"), nullable=True)
    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=True)
    round = Column(String(100))          # 'Gameweek 32', 'Quarter-Final'
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(30), default="scheduled", index=True)
    # status: 'scheduled' | 'live' | 'half_time' | 'finished' | 'postponed' | 'cancelled'
    match_time = Column(String(20))      # '76′', 'HT', 'FT', 'Q3 4:12', 'Day 3'
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    home_score_detail = Column(Text)     # Cricket: '186/6 (18.2)'
    away_score_detail = Column(Text)
    winner_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    sport = relationship("Sport", back_populates="matches")
    league = relationship("League", back_populates="matches")
    season = relationship("Season", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    winner_team = relationship("Team", foreign_keys=[winner_team_id], back_populates="won_matches")
    venue = relationship("Venue", back_populates="matches")
    live_score = relationship("LiveScore", back_populates="match", uselist=False, cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    statistics = relationship("MatchStatistic", back_populates="match", cascade="all, delete-orphan")
    homepage_blocks = relationship("HomepageBlock", back_populates="match")


class LiveScore(Base):
    __tablename__ = "live_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), unique=True, nullable=False)
    match_time = Column(String(20))
    events_text = Column(Text)
    commentary = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    match = relationship("Match", back_populates="live_score")


class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    # goal | card | substitution | wicket | try | point | ko | set
    event_time = Column(String(20))
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="events")
    team = relationship("Team")
    player = relationship("Player", back_populates="match_events")


class MatchStatistic(Base):
    __tablename__ = "match_statistics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    stat_key = Column(String(100), nullable=False)
    stat_value = Column(String(100))

    match = relationship("Match", back_populates="statistics")
    team = relationship("Team")
