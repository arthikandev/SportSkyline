"""
SportSkyline Backend — Pydantic v2 Schemas: Matches, LiveScores, Events, Statistics, Standings
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Match Event ───────────────────────────────────────────────────────────
class MatchEventCreate(BaseModel):
    event_type: str
    event_time: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    player_id: Optional[uuid.UUID] = None
    detail: Optional[str] = None


class MatchEventOut(BaseModel):
    id: uuid.UUID
    event_type: str
    event_time: Optional[str]
    team_id: Optional[uuid.UUID]
    player_id: Optional[uuid.UUID]
    detail: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Match Statistic ───────────────────────────────────────────────────────
class MatchStatCreate(BaseModel):
    team_id: Optional[uuid.UUID] = None
    stat_key: str
    stat_value: str


class MatchStatOut(BaseModel):
    id: uuid.UUID
    team_id: Optional[uuid.UUID]
    stat_key: str
    stat_value: Optional[str]

    model_config = {"from_attributes": True}


# ── Live Score ────────────────────────────────────────────────────────────
class LiveScoreUpdate(BaseModel):
    match_time: Optional[str] = None
    events_text: Optional[str] = None
    commentary: Optional[str] = None


class LiveScoreOut(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID
    match_time: Optional[str]
    events_text: Optional[str]
    commentary: Optional[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Match ─────────────────────────────────────────────────────────────────
class MatchCreate(BaseModel):
    sport_id: uuid.UUID
    league_id: Optional[uuid.UUID] = None
    season_id: Optional[uuid.UUID] = None
    home_team_id: Optional[uuid.UUID] = None
    away_team_id: Optional[uuid.UUID] = None
    venue_id: Optional[uuid.UUID] = None
    round: Optional[str] = None
    scheduled_at: datetime
    status: str = "scheduled"
    is_featured: bool = False


class MatchUpdate(BaseModel):
    league_id: Optional[uuid.UUID] = None
    home_team_id: Optional[uuid.UUID] = None
    away_team_id: Optional[uuid.UUID] = None
    venue_id: Optional[uuid.UUID] = None
    round: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class ScoreUpdate(BaseModel):
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    home_score_detail: Optional[str] = None
    away_score_detail: Optional[str] = None
    match_time: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str  # scheduled | live | half_time | finished | postponed | cancelled
    match_time: Optional[str] = None


class MatchListOut(BaseModel):
    id: uuid.UUID
    sport_id: uuid.UUID
    league_id: Optional[uuid.UUID]
    round: Optional[str]
    scheduled_at: datetime
    status: str
    match_time: Optional[str]
    home_score: int
    away_score: int
    home_score_detail: Optional[str]
    away_score_detail: Optional[str]
    is_featured: bool
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    home_team_logo: Optional[str] = None
    away_team_logo: Optional[str] = None
    league_name: Optional[str] = None
    sport_name: Optional[str] = None
    sport_emoji: Optional[str] = None

    model_config = {"from_attributes": True}


class MatchDetailOut(MatchListOut):
    events: List[MatchEventOut] = []
    statistics: List[MatchStatOut] = []
    live_score: Optional[LiveScoreOut] = None

    model_config = {"from_attributes": True}


# ── Standing ──────────────────────────────────────────────────────────────
class StandingOut(BaseModel):
    id: uuid.UUID
    season_id: uuid.UUID
    team_id: uuid.UUID
    position: Optional[int]
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_diff: int
    points: int
    form: Optional[str]
    team_name: Optional[str] = None
    team_logo: Optional[str] = None

    model_config = {"from_attributes": True}


class StandingUpdate(BaseModel):
    position: Optional[int] = None
    played: Optional[int] = None
    won: Optional[int] = None
    drawn: Optional[int] = None
    lost: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    points: Optional[int] = None
    form: Optional[str] = None
