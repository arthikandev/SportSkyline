"""
SportSkyline Backend — Admin Router: Teams & Players
/api/v1/admin/teams/*
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.models.team import Team, Player
from app.schemas.team import TeamCreate, TeamUpdate, TeamOut, PlayerCreate, PlayerUpdate, PlayerOut
from app.utils.slug import unique_slug
from app.utils.audit import write_audit

router = APIRouter(prefix="/admin/teams", tags=["Admin – Teams & Players"])


@router.get("", response_model=List[TeamOut])
async def list_teams(
    sport_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    stmt = select(Team)
    if sport_id:
        stmt = stmt.where(Team.sport_id == sport_id)
    result = await db.execute(stmt.order_by(Team.name))
    return result.scalars().all()


@router.post("", response_model=TeamOut, status_code=201)
async def create_team(
    payload: TeamCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    async def _slug_exists(s: str) -> bool:
        res = await db.execute(select(Team).where(Team.slug == s))
        return res.scalar_one_or_none() is not None

    slug = await unique_slug(payload.name, _slug_exists)
    team = Team(**payload.model_dump(), slug=slug)
    db.add(team)
    await db.flush()
    await write_audit(db, admin.id, "team.create", "teams", team.id)
    return team


@router.get("/{team_id}/players", response_model=List[PlayerOut])
async def list_players(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(select(Player).where(Player.team_id == team_id))
    return result.scalars().all()
