"""
SportSkyline Backend — Public Router: Matches, Live Scores, Fixtures, Standings
"""
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.match import Match
from app.models.standing import Standing
from app.models.team import Team
from app.repositories.match_repo import MatchRepository
from app.schemas.match import MatchListOut, MatchDetailOut, StandingOut
from app.schemas.system import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(tags=["Public – Matches & Scores"])


# ── Matches ───────────────────────────────────────────────────────────────
@router.get("/matches", response_model=PaginatedResponse)
async def list_matches(
    sport: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    match_date: Optional[date] = Query(None, alias="date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    sport_id = None
    if sport:
        from app.models.sport import Sport
        r = await db.execute(select(Sport).where(Sport.slug == sport))
        s = r.scalar_one_or_none()
        if s:
            sport_id = s.id

    repo = MatchRepository(db)
    offset = (page - 1) * limit
    items, total = await repo.get_by_status(
        status=status, sport_id=sport_id, match_date=match_date,
        offset=offset, limit=limit,
    )
    out = [_match_to_out(m) for m in items]
    return paginate(out, total, page, limit)


@router.get("/matches/live")
async def live_matches(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    sport_id = None
    if sport:
        from app.models.sport import Sport
        r = await db.execute(select(Sport).where(Sport.slug == sport))
        s = r.scalar_one_or_none()
        if s:
            sport_id = s.id
    repo = MatchRepository(db)
    matches = await repo.get_live(sport_id=sport_id)
    return {"matches": [_match_to_out(m) for m in matches]}


@router.get("/live-scores")
async def live_scores_feed(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Live scores feed grouped by sport + league.
    Designed to feed live.html match feed.
    """
    sport_id = None
    if sport:
        from app.models.sport import Sport
        r = await db.execute(select(Sport).where(Sport.slug == sport))
        s = r.scalar_one_or_none()
        if s:
            sport_id = s.id

    repo = MatchRepository(db)
    live = await repo.get_live(sport_id=sport_id)
    upcoming = await repo.get_upcoming(sport_id=sport_id, days=2)

    return {
        "live": [_match_to_live_out(m) for m in live],
        "upcoming": [_match_to_live_out(m) for m in upcoming],
    }


@router.get("/fixtures")
async def upcoming_fixtures(
    sport: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    sport_id = None
    if sport:
        from app.models.sport import Sport
        r = await db.execute(select(Sport).where(Sport.slug == sport))
        s = r.scalar_one_or_none()
        if s:
            sport_id = s.id
    repo = MatchRepository(db)
    items = await repo.get_upcoming(sport_id=sport_id, days=days)
    return {"fixtures": [_match_to_out(m) for m in items]}


@router.get("/matches/{match_id}", response_model=MatchDetailOut)
async def match_detail(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = MatchRepository(db)
    m = await repo.get_with_detail(match_id)
    if not m:
        raise HTTPException(status_code=404, detail="Match not found")
    return _match_to_out(m)


@router.get("/matches/{match_id}/events")
async def match_events(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = MatchRepository(db)
    m = await repo.get_with_detail(match_id)
    if not m:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"events": [{"type": e.event_type, "time": e.event_time, "detail": e.detail} for e in m.events]}


# ── Standings ─────────────────────────────────────────────────────────────
@router.get("/standings/{season_id}")
async def standings(season_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Standing)
        .options(selectinload(Standing.team))
        .where(Standing.season_id == season_id)
        .order_by(Standing.position)
    )
    rows = result.scalars().all()
    return {
        "standings": [
            {
                "position": r.position,
                "team": r.team.name if r.team else None,
                "team_logo": r.team.logo_url if r.team else None,
                "played": r.played,
                "won": r.won,
                "drawn": r.drawn,
                "lost": r.lost,
                "goals_for": r.goals_for,
                "goals_against": r.goals_against,
                "goal_diff": r.goal_diff,
                "points": r.points,
                "form": r.form,
            }
            for r in rows
        ]
    }


# ── Helpers ───────────────────────────────────────────────────────────────
def _match_to_out(m: Match) -> dict:
    return {
        "id": str(m.id),
        "sport_id": str(m.sport_id),
        "sport": m.sport.name if m.sport else None,
        "sport_emoji": m.sport.emoji if m.sport else None,
        "sport_slug": m.sport.slug if m.sport else None,
        "league": m.league.name if m.league else None,
        "league_id": str(m.league_id) if m.league_id else None,
        "round": m.round,
        "scheduled_at": m.scheduled_at.isoformat(),
        "status": m.status,
        "match_time": m.match_time,
        "home_team": m.home_team.name if m.home_team else None,
        "home_team_short": m.home_team.short_name if m.home_team else None,
        "home_team_logo": m.home_team.logo_url if m.home_team else None,
        "away_team": m.away_team.name if m.away_team else None,
        "away_team_short": m.away_team.short_name if m.away_team else None,
        "away_team_logo": m.away_team.logo_url if m.away_team else None,
        "home_score": m.home_score,
        "away_score": m.away_score,
        "home_score_detail": m.home_score_detail,
        "away_score_detail": m.away_score_detail,
        "is_featured": m.is_featured,
    }


def _match_to_live_out(m: Match) -> dict:
    out = _match_to_out(m)
    if m.live_score:
        out["events_text"] = m.live_score.events_text
        out["commentary"] = m.live_score.commentary
    return out
