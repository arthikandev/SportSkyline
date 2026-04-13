"""
SportSkyline Backend — Pydantic v2 Schemas: Sports, Leagues, Seasons, Venues
"""
from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Sport ─────────────────────────────────────────────────────────────────
class SportCreate(BaseModel):
    name: str = Field(..., max_length=100)
    emoji: Optional[str] = None
    icon_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class SportUpdate(BaseModel):
    name: Optional[str] = None
    emoji: Optional[str] = None
    icon_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SportOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    emoji: Optional[str]
    icon_url: Optional[str]
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


# ── League ────────────────────────────────────────────────────────────────
class LeagueCreate(BaseModel):
    sport_id: uuid.UUID
    name: str = Field(..., max_length=200)
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class LeagueUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class LeagueOut(BaseModel):
    id: uuid.UUID
    sport_id: uuid.UUID
    name: str
    slug: str
    short_name: Optional[str]
    logo_url: Optional[str]
    country: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


# ── Season ────────────────────────────────────────────────────────────────
class SeasonCreate(BaseModel):
    league_id: uuid.UUID
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


class SeasonOut(BaseModel):
    id: uuid.UUID
    league_id: uuid.UUID
    name: str
    start_date: Optional[date]
    end_date: Optional[date]
    is_current: bool

    model_config = {"from_attributes": True}


# ── Venue ─────────────────────────────────────────────────────────────────
class VenueCreate(BaseModel):
    name: str = Field(..., max_length=200)
    city: Optional[str] = None
    country: Optional[str] = None
    capacity: Optional[int] = None
    surface: Optional[str] = None
    image_url: Optional[str] = None


class VenueOut(BaseModel):
    id: uuid.UUID
    name: str
    city: Optional[str]
    country: Optional[str]
    capacity: Optional[int]
    surface: Optional[str]
    image_url: Optional[str]

    model_config = {"from_attributes": True}
