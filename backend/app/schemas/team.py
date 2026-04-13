"""
SportSkyline Backend — Pydantic v2 Schemas: Teams, Players
"""
from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Team ──────────────────────────────────────────────────────────────────
class TeamCreate(BaseModel):
    sport_id: uuid.UUID
    name: str = Field(..., max_length=200)
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    founded_year: Optional[int] = None
    is_active: bool = True


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    founded_year: Optional[int] = None
    is_active: Optional[bool] = None


class TeamOut(BaseModel):
    id: uuid.UUID
    sport_id: uuid.UUID
    name: str
    short_name: Optional[str]
    slug: str
    logo_url: Optional[str]
    country: Optional[str]
    city: Optional[str]
    founded_year: Optional[int]
    is_active: bool

    model_config = {"from_attributes": True}


# ── Player ────────────────────────────────────────────────────────────────
class PlayerCreate(BaseModel):
    team_id: Optional[uuid.UUID] = None
    name: str = Field(..., max_length=200)
    position: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    jersey_number: Optional[int] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True


class PlayerUpdate(BaseModel):
    team_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    position: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    jersey_number: Optional[int] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class PlayerOut(BaseModel):
    id: uuid.UUID
    team_id: Optional[uuid.UUID]
    name: str
    slug: str
    position: Optional[str]
    nationality: Optional[str]
    date_of_birth: Optional[date]
    jersey_number: Optional[int]
    photo_url: Optional[str]
    bio: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
