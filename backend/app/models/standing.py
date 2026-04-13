"""
SportSkyline Backend — ORM Models: Standing
"""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Standing(Base):
    __tablename__ = "standings"
    __table_args__ = (UniqueConstraint("season_id", "team_id", name="uq_standing_season_team"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey("seasons.id"), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    position = Column(Integer)
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    points = Column(Integer, default=0)
    form = Column(String(20))  # 'WWDLW'
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    season = relationship("Season", back_populates="standings")
    team = relationship("Team", back_populates="standings")

    @property
    def goal_diff(self) -> int:
        return (self.goals_for or 0) - (self.goals_against or 0)
