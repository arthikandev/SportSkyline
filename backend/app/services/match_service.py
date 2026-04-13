"""
SportSkyline Backend — Match Service
Handles match CRUD, live score updates, event management.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, LiveScore, MatchEvent
from app.repositories.match_repo import MatchRepository
from app.schemas.match import MatchCreate, MatchUpdate, ScoreUpdate, StatusUpdate, LiveScoreUpdate, MatchEventCreate
from app.utils.audit import write_audit


class MatchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = MatchRepository(db)

    async def create(self, payload: MatchCreate, admin_id: Optional[uuid.UUID] = None) -> Match:
        data = payload.model_dump()
        match = await self.repo.create(data)
        await write_audit(self.db, admin_id, "match.create", "matches", match.id)
        return match

    async def update(self, match_id: uuid.UUID, payload: MatchUpdate, admin_id: Optional[uuid.UUID] = None) -> Match:
        match = await self.repo.get(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        updated = await self.repo.update(match_id, payload.model_dump(exclude_none=True))
        await write_audit(self.db, admin_id, "match.update", "matches", match_id)
        return updated

    async def update_score(self, match_id: uuid.UUID, payload: ScoreUpdate, admin_id: Optional[uuid.UUID] = None) -> Match:
        match = await self.repo.get(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        match.home_score = payload.home_score
        match.away_score = payload.away_score
        if payload.home_score_detail:
            match.home_score_detail = payload.home_score_detail
        if payload.away_score_detail:
            match.away_score_detail = payload.away_score_detail
        if payload.match_time:
            match.match_time = payload.match_time
        match.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await write_audit(
            self.db, admin_id, "match.score_update", "matches", match_id,
            new_data={"home_score": payload.home_score, "away_score": payload.away_score}
        )
        return match

    async def update_status(self, match_id: uuid.UUID, payload: StatusUpdate, admin_id: Optional[uuid.UUID] = None) -> Match:
        match = await self.repo.get(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        match.status = payload.status
        if payload.match_time:
            match.match_time = payload.match_time
        await self.db.flush()
        await write_audit(self.db, admin_id, "match.status_update", "matches", match_id,
                          new_data={"status": payload.status})
        return match

    async def add_event(self, match_id: uuid.UUID, payload: MatchEventCreate, admin_id: Optional[uuid.UUID] = None) -> MatchEvent:
        match = await self.repo.get(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        event = MatchEvent(match_id=match_id, **payload.model_dump())
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def update_live_score(self, match_id: uuid.UUID, payload: LiveScoreUpdate) -> LiveScore:
        from sqlalchemy import select
        result = await self.db.execute(select(LiveScore).where(LiveScore.match_id == match_id))
        live = result.scalar_one_or_none()
        if not live:
            live = LiveScore(match_id=match_id)
            self.db.add(live)

        if payload.match_time is not None:
            live.match_time = payload.match_time
        if payload.events_text is not None:
            live.events_text = payload.events_text
        if payload.commentary is not None:
            live.commentary = payload.commentary
        live.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(live)
        return live

    async def delete(self, match_id: uuid.UUID, admin_id: Optional[uuid.UUID] = None) -> None:
        success = await self.repo.hard_delete(match_id)
        if not success:
            raise HTTPException(status_code=404, detail="Match not found")
        await write_audit(self.db, admin_id, "match.delete", "matches", match_id)
