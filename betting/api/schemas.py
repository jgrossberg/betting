from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from betting.models.enums import GameStatus, BetType, BetSelection, BetStatus


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    home_team: str
    away_team: str
    commence_time: datetime
    status: GameStatus
    home_moneyline: Decimal | None
    away_moneyline: Decimal | None
    home_spread: Decimal | None
    home_spread_odds: Decimal | None
    away_spread: Decimal | None
    away_spread_odds: Decimal | None
    total_points: Decimal | None
    over_odds: Decimal | None
    under_odds: Decimal | None
    home_score: int | None
    away_score: int | None


class PlaceBetRequest(BaseModel):
    game_id: UUID
    bet_type: BetType
    selection: BetSelection
    stake: Decimal


class BetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    game_id: UUID
    bet_type: BetType
    selection: BetSelection
    odds: Decimal
    stake: Decimal
    potential_payout: Decimal
    status: BetStatus
    settled_at: datetime | None


class BalanceResponse(BaseModel):
    user_id: UUID
    balance: Decimal


class CreateUserRequest(BaseModel):
    username: str
    balance: Decimal = Decimal("1000.00")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    balance: Decimal


class ErrorResponse(BaseModel):
    detail: str
