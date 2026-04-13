"""
SportSkyline Backend — Admin Router: Sports & Leagues
/api/v1/admin/sports/*
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.models.sport import Sport, League, Season
from app.schemas.sport import (
    SportCreate, SportUpdate, SportOut,
    LeagueCreate, LeagueUpdate, LeagueOut,
    SeasonCreate, SeasonOut
)
from app.utils.slug import unique_slug
from app.utils.audit import write_audit

router = APIRouter(prefix="/admin/sports", tags=["Admin – Sports & Leagues"])


# ── Sports ────────────────────────────────────────────────────────────────
@router.get("", response_model=List[SportOut])
async def list_sports(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(select(Sport).order_by(Sport.sort_order))
    return result.scalars().all()


@router.post("", response_model=SportOut, status_code=201)
async def create_sport(
    payload: SportCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    async def _slug_exists(s: str) -> bool:
        res = await db.execute(select(Sport).where(Sport.slug == s))
        return res.scalar_one_or_none() is not None

    slug = await unique_slug(payload.name, _slug_exists)
    sport = Sport(**payload.model_dump(), slug=slug)
    db.add(sport)
    await db.flush()
    await write_audit(db, admin.id, "sport.create", "sports", sport.id)
    return sport


@router.put("/{sport_id}", response_model=SportOut)
async def update_sport(
    sport_id: uuid.UUID,
    payload: SportUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(sport, k, v)
    
    await db.flush()
    await write_audit(db, admin.id, "sport.update", "sports", sport_id)
    return sport


# ── Leagues ───────────────────────────────────────────────────────────────
@router.get("/{sport_id}/leagues", response_model=List[LeagueOut])
async def list_leagues(
    sport_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(League).where(League.sport_id == sport_id).order_by(League.sort_order)
    )
    return result.scalars().all()


@router.post("/leagues", response_model=LeagueOut, status_code=201)
async def create_league(
    payload: LeagueCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    async def _slug_exists(s: str) -> bool:
        res = await db.execute(select(League).where(League.slug == s))
        return res.scalar_one_or_none() is not None

    slug = await unique_slug(payload.name, _slug_exists)
    league = League(**payload.model_dump(), slug=slug)
    db.add(league)
    await db.flush()
    await write_audit(db, admin.id, "league.create", "leagues", league.id)
    return league
