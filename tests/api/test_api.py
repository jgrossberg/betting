from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from betting.api.http_api import app, get_session
from betting.models.base import Base
from betting.models.game import Game, GameStatus
from betting.models.user import User
from betting.models.enums import BetStatus


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(engine):
    Session = sessionmaker(bind=engine)

    def override_get_session():
        session = Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user(db_session):
    user = User(username="testuser", balance=Decimal("1000.00"))
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def game(db_session):
    game = Game(
        external_id="test_game_1",
        home_team="Lakers",
        away_team="Warriors",
        commence_time=datetime.now(timezone.utc) + timedelta(hours=2),
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
    return game


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_games_empty(client):
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == []


def test_list_games_returns_all_by_default(client, game, db_session):
    """Without status filter, returns all games regardless of status."""
    # Create a completed game
    completed_game = Game(
        external_id="completed_game_1",
        home_team="Celtics",
        away_team="Heat",
        commence_time=datetime.now(timezone.utc) - timedelta(hours=24),
        home_moneyline=Decimal("-110"),
        away_moneyline=Decimal("100"),
        home_spread=Decimal("-3.5"),
        home_spread_odds=Decimal("-110"),
        away_spread=Decimal("3.5"),
        away_spread_odds=Decimal("-110"),
        total_points=Decimal("210.5"),
        over_odds=Decimal("-110"),
        under_odds=Decimal("-110"),
        status=GameStatus.COMPLETED,
    )
    db_session.add(completed_game)
    db_session.commit()

    response = client.get("/games")
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 2  # Both upcoming and completed


def test_list_games_filter_by_status_upcoming(client, game, db_session):
    """With status=upcoming, returns only upcoming games."""
    completed_game = Game(
        external_id="completed_game_2",
        home_team="Celtics",
        away_team="Heat",
        commence_time=datetime.now(timezone.utc) - timedelta(hours=24),
        home_moneyline=Decimal("-110"),
        away_moneyline=Decimal("100"),
        home_spread=Decimal("-3.5"),
        home_spread_odds=Decimal("-110"),
        away_spread=Decimal("3.5"),
        away_spread_odds=Decimal("-110"),
        total_points=Decimal("210.5"),
        over_odds=Decimal("-110"),
        under_odds=Decimal("-110"),
        status=GameStatus.COMPLETED,
    )
    db_session.add(completed_game)
    db_session.commit()

    response = client.get("/games?status=upcoming")
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 1
    assert games[0]["status"] == "upcoming"


def test_list_games_filter_by_status_completed(client, game, db_session):
    """With status=completed, returns only completed games."""
    game.status = GameStatus.COMPLETED
    db_session.commit()

    response = client.get("/games?status=completed")
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 1
    assert games[0]["status"] == "completed"


def test_place_bet_success(client, user, game):
    response = client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(game.id),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "100.00",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stake"] == "100.00"
    assert data["bet_type"] == "moneyline"
    assert data["selection"] == "home"
    assert data["status"] == "pending"


def test_place_bet_insufficient_balance(client, user, game):
    response = client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(game.id),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "5000.00",
        },
    )
    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]


def test_place_bet_invalid_game(client, user):
    response = client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(uuid4()),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "100.00",
        },
    )
    assert response.status_code == 400
    assert "Game not found" in response.json()["detail"]


def test_place_bet_game_already_started(client, user, game, db_session):
    game.status = GameStatus.IN_PROGRESS
    db_session.commit()

    response = client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(game.id),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "100.00",
        },
    )
    assert response.status_code == 400
    assert "already started" in response.json()["detail"]


def test_get_user_bets_empty(client, user):
    response = client.get(f"/users/{user.id}/bets")
    assert response.status_code == 200
    assert response.json() == []


def test_get_user_bets_with_bets(client, user, game):
    client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(game.id),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "100.00",
        },
    )

    response = client.get(f"/users/{user.id}/bets")
    assert response.status_code == 200
    bets = response.json()
    assert len(bets) == 1
    assert bets[0]["stake"] == "100.00"


def test_get_balance(client, user):
    response = client.get(f"/users/{user.id}/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "1000.00"
    assert data["user_id"] == str(user.id)


def test_get_balance_user_not_found(client):
    response = client.get(f"/users/{uuid4()}/balance")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_balance_decreases_after_bet(client, user, game):
    client.post(
        "/bets",
        params={"user_id": str(user.id)},
        json={
            "game_id": str(game.id),
            "bet_type": "moneyline",
            "selection": "home",
            "stake": "100.00",
        },
    )

    response = client.get(f"/users/{user.id}/balance")
    assert response.status_code == 200
    assert response.json()["balance"] == "900.00"


def test_create_user(client):
    response = client.post(
        "/users",
        json={"username": "newuser"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["balance"] == "1000.00"
    assert "id" in data


def test_create_user_custom_balance(client):
    response = client.post(
        "/users",
        json={"username": "richuser", "balance": "5000.00"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "5000.00"


def test_create_user_duplicate_username(client):
    client.post("/users", json={"username": "dupeuser"})
    response = client.post("/users", json={"username": "dupeuser"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_user_by_username(client, user):
    response = client.get(f"/users/by-username/{user.username}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["id"] == str(user.id)
    assert data["balance"] == "1000.00"


def test_get_user_by_username_not_found(client):
    response = client.get("/users/by-username/nonexistent")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_user_by_username_special_chars(client):
    # Create user with special characters
    response = client.post("/users", json={"username": "user@test.com"})
    assert response.status_code == 200

    # Should be able to look up with URL encoding
    response = client.get("/users/by-username/user%40test.com")
    assert response.status_code == 200
    assert response.json()["username"] == "user@test.com"


def test_admin_fetch_games_requires_auth(client):
    response = client.post("/admin/fetch-games")
    assert response.status_code == 422


def test_admin_fetch_games_rejects_bad_key(client):
    response = client.post(
        "/admin/fetch-games",
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert response.status_code == 401
    assert "Invalid admin key" in response.json()["detail"]


def test_admin_score_games_requires_auth(client):
    response = client.post("/admin/score-games")
    assert response.status_code == 422


def test_admin_score_games_rejects_bad_key(client):
    response = client.post(
        "/admin/score-games",
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_admin_settle_bets_requires_auth(client):
    response = client.post("/admin/settle-bets")
    assert response.status_code == 422


def test_admin_settle_bets_rejects_bad_key(client):
    response = client.post(
        "/admin/settle-bets",
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert response.status_code == 401


@patch("betting.api.http_api.config")
@patch("betting.api.http_api.GameSyncService")
def test_admin_fetch_games_success(mock_sync_service, mock_config, client):
    mock_config.ADMIN_API_KEY = "test-key"
    mock_service_instance = MagicMock()
    mock_service_instance.sync_games.return_value = {
        "created": 5,
        "updated": 2,
        "total": 7,
    }
    mock_sync_service.return_value = mock_service_instance

    response = client.post(
        "/admin/fetch-games",
        headers={"X-Admin-Key": "test-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["created"] == 5
    assert data["updated"] == 2
    assert data["total"] == 7
    mock_service_instance.sync_games.assert_called_once()


@patch("betting.api.http_api.config")
@patch("betting.api.http_api.GameScoringService")
def test_admin_score_games_success(mock_scoring_service, mock_config, client):
    mock_config.ADMIN_API_KEY = "test-key"
    mock_service_instance = MagicMock()
    mock_service_instance.update_completed_games.return_value = [
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]
    mock_scoring_service.return_value = mock_service_instance

    response = client.post(
        "/admin/score-games",
        headers={"X-Admin-Key": "test-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["games_updated"] == 3
    mock_service_instance.update_completed_games.assert_called_once_with(days_from=2)


@patch("betting.api.http_api.config")
@patch("betting.api.http_api.BetSettlementService")
@patch("betting.api.http_api.GameRepository")
def test_admin_settle_bets_success(
    mock_game_repo, mock_settlement_service, mock_config, client
):
    mock_config.ADMIN_API_KEY = "test-key"

    mock_repo_instance = MagicMock()
    mock_repo_instance.find_games_with_pending_bets.return_value = [MagicMock()]
    mock_game_repo.return_value = mock_repo_instance

    mock_won_bet = MagicMock()
    mock_won_bet.status = BetStatus.WON
    mock_lost_bet = MagicMock()
    mock_lost_bet.status = BetStatus.LOST
    mock_push_bet = MagicMock()
    mock_push_bet.status = BetStatus.PUSH

    mock_service_instance = MagicMock()
    mock_service_instance.settle_bets_for_games.return_value = [
        mock_won_bet,
        mock_won_bet,
        mock_lost_bet,
        mock_push_bet,
    ]
    mock_settlement_service.return_value = mock_service_instance

    response = client.post(
        "/admin/settle-bets",
        headers={"X-Admin-Key": "test-key"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["bets_settled"] == 4
    assert data["won"] == 2
    assert data["lost"] == 1
    assert data["push"] == 1
