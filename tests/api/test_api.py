from datetime import datetime, timedelta
from decimal import Decimal
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
        commence_time=datetime.now() + timedelta(hours=2),
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


def test_list_games_returns_upcoming(client, game):
    response = client.get("/games")
    assert response.status_code == 200
    games = response.json()
    assert len(games) == 1
    assert games[0]["home_team"] == "Lakers"
    assert games[0]["away_team"] == "Warriors"
    assert games[0]["status"] == "upcoming"


def test_list_games_filter_by_status(client, game, db_session):
    game.status = GameStatus.COMPLETED
    db_session.commit()

    response = client.get("/games?status=upcoming")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/games?status=completed")
    assert response.status_code == 200
    assert len(response.json()) == 1


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
