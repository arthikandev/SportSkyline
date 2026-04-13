"""
SportSkyline Backend — Admin Router: Matches & Live Scores
/api/v1/admin/matches/*
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchListOut, MatchDetailOut,
    ScoreUpdate, StatusUpdate, LiveScoreUpdate, MatchEventCreate
)
from app.services.match_service import MatchService

router = APIRouter(prefix="/admin/matches", tags=["Admin – Matches & Scores"])


@router.post("", response_model=MatchDetailOut, status_code=201)
async def create_match(
    payload: MatchCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    service = MatchService(db)
    match = await service.create(payload, admin_id=admin.id)
    # Re-fetch with details
    return await service.repo.get_with_detail(match.id)


@router.patch("/{match_id}/score", response_model=MatchDetailOut)
async def update_match_score(
    match_id: uuid.UUID,
    payload: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    service = MatchService(db)
    match = await service.update_score(match_id, payload, admin_id=admin.id)
    return await service.repo.get_with_detail(match.id)


@router.patch("/{match_id}/status")
async def update_match_status(
    match_id: uuid.UUID,
    payload: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    service = MatchService(db)
    await service.update_status(match_id, payload, admin_id=admin.id)
    return {"status": "updated"}


@router.post("/{match_id}/events")
async def add_match_event(
    match_id: uuid.UUID,
    payload: MatchEventCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    service = MatchService(db)
    await service.add_event(match_id, payload, admin_id=admin.id)
    return {"status": "created"}
