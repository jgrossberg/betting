from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, Numeric, Integer, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .base import Base


class GameStatus(PyEnum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Teams
    home_team: Mapped[str] = mapped_column(String(100), nullable=False)
    away_team: Mapped[str] = mapped_column(String(100), nullable=False)

    # Game timing
    commence_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Moneyline odds (American format, e.g., +150, -110)
    home_moneyline: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    away_moneyline: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Spread betting
    home_spread: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    home_spread_odds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    away_spread: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    away_spread_odds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Over/Under (Totals)
    total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    over_odds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    under_odds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Final scores (null until game completes)
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), nullable=False, default=GameStatus.UPCOMING
    )

    def __repr__(self):
        return f"<Game(id={self.id}, {self.away_team} @ {self.home_team}, {self.commence_time})>"
