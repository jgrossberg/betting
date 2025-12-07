from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from betting.database import get_database
from betting.config import config
from betting.models.enums import BetSelection, BetType, GameStatus, BetStatus
from betting.repositories import GameRepository, UserRepository
from betting.services import BettingService, InsufficientBalanceError, InvalidBetError
from betting.services.game_sync_service import GameSyncService
from betting.services import GameScoringService, BetSettlementService

from .schemas import (
    GameResponse,
    PlaceBetRequest,
    BetResponse,
    BalanceResponse,
    CreateUserRequest,
    UserResponse,
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


def has_all_lines(game) -> bool:
    """Check if game has all betting lines available."""
    return all([
        game.home_moneyline is not None,
        game.away_moneyline is not None,
        game.home_spread is not None,
        game.away_spread is not None,
        game.total_points is not None,
    ])


@app.get("/games", response_model=list[GameResponse])
def list_games(
    status: GameStatus | None = None,
    session: Session = Depends(get_session),
):
    game_repo = GameRepository(session)

    if status:
        games = game_repo.find_by_status(status)
    else:
        games = game_repo.find_all()

    # Filter out games without complete betting lines
    games = [g for g in games if has_all_lines(g)]

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


@app.get("/users/by-username/{username}", response_model=UserResponse)
def get_user_by_username(
    username: str,
    session: Session = Depends(get_session),
):
    user_repo = UserRepository(session)
    user = user_repo.find_by_username(username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/users", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    session: Session = Depends(get_session),
):
    user_repo = UserRepository(session)

    existing = user_repo.find_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = user_repo.create(username=request.username, balance=request.balance)
    return user


def verify_admin_key(x_admin_key: str = Header()):
    if not config.ADMIN_API_KEY:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY not configured")
    if x_admin_key != config.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


@app.post("/admin/fetch-games")
def admin_fetch_games(
    session: Session = Depends(get_session),
    _: None = Depends(verify_admin_key),
):
    sync_service = GameSyncService(session)
    result = sync_service.sync_games()

    return {
        "status": "success",
        "created": result["created"],
        "updated": result["updated"],
        "total": result["total"],
    }


@app.post("/admin/score-games")
def admin_score_games(
    session: Session = Depends(get_session),
    _: None = Depends(verify_admin_key),
):
    scoring_service = GameScoringService(session)
    updated_games = scoring_service.update_completed_games(days_from=2)

    return {
        "status": "success",
        "games_updated": len(updated_games),
    }


@app.post("/admin/settle-bets")
def admin_settle_bets(
    session: Session = Depends(get_session),
    _: None = Depends(verify_admin_key),
):
    game_repo = GameRepository(session)
    finished_games = game_repo.find_games_with_pending_bets(GameStatus.COMPLETED)

    settlement_service = BetSettlementService(session)
    settled_bets = settlement_service.settle_bets_for_games(finished_games)

    won_count = sum(1 for bet in settled_bets if bet.status == BetStatus.WON)
    lost_count = sum(1 for bet in settled_bets if bet.status == BetStatus.LOST)
    push_count = sum(1 for bet in settled_bets if bet.status == BetStatus.PUSH)

    return {
        "status": "success",
        "bets_settled": len(settled_bets),
        "won": won_count,
        "lost": lost_count,
        "push": push_count,
    }
