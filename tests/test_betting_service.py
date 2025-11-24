from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, User, Game, Bet, BetType, BetSelection, BetStatus, GameStatus
from src.services import BettingService, InsufficientBalanceError, InvalidBetError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user(db_session):
    user = User(username="testuser", balance=Decimal("1000.00"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def game(db_session):
    game = Game(
        external_id="test_game_1",
        home_team="Lakers",
        away_team="Warriors",
        commence_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=2),
        home_moneyline=Decimal("-110"),
        away_moneyline=Decimal("120"),
        home_spread=Decimal("-5.5"),
        home_spread_odds=Decimal("-110"),
        away_spread=Decimal("5.5"),
        away_spread_odds=Decimal("-110"),
        total_points=Decimal("215.5"),
        over_odds=Decimal("-110"),
        under_odds=Decimal("-110"),
        status=GameStatus.UPCOMING,
    )
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game


class TestPlaceBet:
    def test_place_moneyline_bet(self, db_session, user, game):
        service = BettingService(db_session)

        bet = service.place_bet(
            user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
        )

        assert bet.user_id == user.id
        assert bet.game_id == game.id
        assert bet.bet_type == BetType.MONEYLINE
        assert bet.selection == BetSelection.HOME
        assert bet.stake == Decimal("100")
        assert bet.odds == Decimal("-110")
        assert bet.status == BetStatus.PENDING

        db_session.refresh(user)
        assert user.balance == Decimal("900.00")

    def test_place_spread_bet(self, db_session, user, game):
        service = BettingService(db_session)

        bet = service.place_bet(
            user.id, game.id, BetType.SPREAD, BetSelection.AWAY, Decimal("50")
        )

        assert bet.bet_type == BetType.SPREAD
        assert bet.selection == BetSelection.AWAY
        assert bet.odds == Decimal("-110")

    def test_insufficient_balance(self, db_session, user, game):
        service = BettingService(db_session)

        with pytest.raises(InsufficientBalanceError):
            service.place_bet(
                user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("1500")
            )

    def test_negative_stake(self, db_session, user, game):
        service = BettingService(db_session)

        with pytest.raises(InvalidBetError, match="Stake must be greater than 0"):
            service.place_bet(
                user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("-10")
            )

    def test_bet_on_started_game(self, db_session, user, game):
        game.status = GameStatus.IN_PROGRESS
        db_session.commit()

        service = BettingService(db_session)

        with pytest.raises(InvalidBetError, match="already started"):
            service.place_bet(
                user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
            )

    def test_bet_on_past_game(self, db_session, user, game):
        game.commence_time = datetime.now() - timedelta(hours=1)
        db_session.commit()

        service = BettingService(db_session)

        with pytest.raises(InvalidBetError, match="already started"):
            service.place_bet(
                user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
            )

    def test_odds_not_available(self, db_session, user, game):
        game.home_moneyline = None
        db_session.commit()

        service = BettingService(db_session)

        with pytest.raises(InvalidBetError, match="Odds not available"):
            service.place_bet(
                user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
            )


class TestGetUserBalance:
    def test_get_balance(self, db_session, user):
        service = BettingService(db_session)
        balance = service.get_user_balance(user.id)
        assert balance == Decimal("1000.00")


class TestGetBets:
    def test_get_pending_bets(self, db_session, user, game):
        service = BettingService(db_session)

        service.place_bet(
            user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
        )
        service.place_bet(
            user.id, game.id, BetType.SPREAD, BetSelection.AWAY, Decimal("50")
        )

        pending_bets = service.get_pending_bets(user.id)
        assert len(pending_bets) == 2

    def test_get_bet_history(self, db_session, user, game):
        service = BettingService(db_session)

        service.place_bet(
            user.id, game.id, BetType.MONEYLINE, BetSelection.HOME, Decimal("100")
        )

        history = service.get_bet_history(user.id)
        assert len(history) == 1
