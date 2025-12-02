from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from betting.database import get_database
from betting.config import config
from betting.models.enums import BetSelection, BetType, GameStatus
from betting.repositories import GameRepository, UserRepository
from betting.services import BettingService, InsufficientBalanceError, InvalidBetError

from .schemas import (
    GameResponse,
    PlaceBetRequest,
    BetResponse,
    BalanceResponse,
)

app = FastAPI(
    title="Betting API",
    description="NBA Betting API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_db = None


def get_db():
    global _db
    if _db is None:
        _db = get_database(config.DATABASE_URL)
    return _db


def get_session():
    db = get_db()
    with db.get_session() as session:
        yield session


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/games", response_model=list[GameResponse])
def list_games(
    status: GameStatus | None = None,
    session: Session = Depends(get_session),
):
    game_repo = GameRepository(session)

    if status:
        db_status = GameStatus(status.value)
        games = game_repo.find_by_status(db_status)
    else:
        games = game_repo.find_by_status(GameStatus.UPCOMING)

    return games


@app.post("/bets", response_model=BetResponse)
def place_bet(
    request: PlaceBetRequest,
    user_id: UUID,
    session: Session = Depends(get_session),
):
    service = BettingService(session)

    db_bet_type = BetType(request.bet_type.value)
    db_selection = BetSelection(request.selection.value)

    try:
        bet = service.place_bet(
            user_id=user_id,
            game_id=request.game_id,
            bet_type=db_bet_type,
            selection=db_selection,
            stake=request.stake,
        )
        return bet
    except InsufficientBalanceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidBetError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}/bets", response_model=list[BetResponse])
def get_user_bets(
    user_id: UUID,
    session: Session = Depends(get_session),
):
    service = BettingService(session)

    try:
        bets = service.get_bet_history(user_id)
        return bets
    except InvalidBetError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/users/{user_id}/balance", response_model=BalanceResponse)
def get_user_balance(
    user_id: UUID,
    session: Session = Depends(get_session),
):
    user_repo = UserRepository(session)
    user = user_repo.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return BalanceResponse(user_id=user.id, balance=user.balance)
