"""
SportSkyline Backend — Match Repository
Handles live score queries, fixtures by sport/status/date.
"""
from __future__ import annotations
import uuid
from datetime import date, datetime, timezone, timedelta
from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select, desc, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, LiveScore
from app.models.team import Team
from app.models.sport import Sport, League
from app.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Match, db)

    def _base_query(self):
        return (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.sport),
                selectinload(Match.league),
                selectinload(Match.live_score),
                selectinload(Match.events),
            )
        )

    async def get_by_status(
        self,
        status: Optional[str] = None,
        sport_id: Optional[uuid.UUID] = None,
        league_id: Optional[uuid.UUID] = None,
        match_date: Optional[date] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[Match], int]:
        stmt = self._base_query()
        count_stmt = select(func.count()).select_from(Match)

        if status:
            stmt = stmt.where(Match.status == status)
            count_stmt = count_stmt.where(Match.status == status)
        if sport_id:
            stmt = stmt.where(Match.sport_id == sport_id)
            count_stmt = count_stmt.where(Match.sport_id == sport_id)
        if league_id:
            stmt = stmt.where(Match.league_id == league_id)
            count_stmt = count_stmt.where(Match.league_id == league_id)
        if match_date:
            day_start = datetime.combine(match_date, datetime.min.time())
            day_end = datetime.combine(match_date, datetime.max.time())
            stmt = stmt.where(Match.scheduled_at.between(day_start, day_end))
            count_stmt = count_stmt.where(Match.scheduled_at.between(day_start, day_end))

        stmt = stmt.order_by(Match.scheduled_at).offset(offset).limit(limit)
        total = (await self.db.execute(count_stmt)).scalar_one()
        items = (await self.db.execute(stmt)).scalars().all()
        return items, total

    async def get_live(self, sport_id: Optional[uuid.UUID] = None) -> Sequence[Match]:
        stmt = self._base_query().where(Match.status.in_(["live", "half_time"]))
        if sport_id:
            stmt = stmt.where(Match.sport_id == sport_id)
        stmt = stmt.order_by(Match.scheduled_at)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_upcoming(
        self,
        sport_id: Optional[uuid.UUID] = None,
        days: int = 7,
    ) -> Sequence[Match]:
        now = datetime.now(timezone.utc)
        until = now + timedelta(days=days)
        stmt = (
            self._base_query()
            .where(
                Match.status == "scheduled",
                Match.scheduled_at >= now,
                Match.scheduled_at <= until,
            )
        )
        if sport_id:
            stmt = stmt.where(Match.sport_id == sport_id)
        stmt = stmt.order_by(Match.scheduled_at).limit(20)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_with_detail(self, match_id: uuid.UUID) -> Optional[Match]:
        stmt = (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.sport),
                selectinload(Match.league),
                selectinload(Match.venue),
                selectinload(Match.live_score),
                selectinload(Match.events),
                selectinload(Match.statistics),
            )
            .where(Match.id == match_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
