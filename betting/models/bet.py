from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import DateTime, Numeric, Enum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from betting.models.enums import BetSelection, BetStatus, BetType

from .base import Base


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"), nullable=False)

    bet_type: Mapped[BetType] = mapped_column(Enum(BetType), nullable=False)
    selection: Mapped[BetSelection] = mapped_column(Enum(BetSelection), nullable=False)

    odds: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    stake: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    potential_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[BetStatus] = mapped_column(
        Enum(BetStatus), nullable=False, default=BetStatus.PENDING
    )
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Bet(id={self.id}, type={self.bet_type.value}, stake={self.stake}, status={self.status.value})>"
