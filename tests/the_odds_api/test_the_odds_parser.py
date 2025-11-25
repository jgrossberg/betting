from decimal import Decimal
from datetime import datetime
import pytest
from src.the_odds_api.parser import OddsParser
from src.models import GameStatus


def test_parse_complete_game():
    game_data = {
        "id": "test123",
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "commence_time": "2024-01-15T19:00:00Z",
        "bookmakers": [
            {
                "key": "betmgm",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Los Angeles Lakers", "price": -110},
                            {"name": "Golden State Warriors", "price": 120},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {
                                "name": "Los Angeles Lakers",
                                "price": -110,
                                "point": -5.5,
                            },
                            {
                                "name": "Golden State Warriors",
                                "price": -110,
                                "point": 5.5,
                            },
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": -110, "point": 215.5},
                            {"name": "Under", "price": -110, "point": 215.5},
                        ],
                    },
                ],
            }
        ],
    }

    result = OddsParser.parse_game(game_data)

    assert result["external_id"] == "test123"
    assert result["home_team"] == "Los Angeles Lakers"
    assert result["away_team"] == "Golden State Warriors"
    assert isinstance(result["commence_time"], datetime)
    assert result["status"] == GameStatus.UPCOMING

    assert result["home_moneyline"] == Decimal("-110")
    assert result["away_moneyline"] == Decimal("120")
    assert result["home_spread"] == Decimal("-5.5")
    assert result["home_spread_odds"] == Decimal("-110")
    assert result["away_spread"] == Decimal("5.5")
    assert result["away_spread_odds"] == Decimal("-110")
    assert result["total_points"] == Decimal("215.5")
    assert result["over_odds"] == Decimal("-110")
    assert result["under_odds"] == Decimal("-110")


def test_parse_game_missing_bookmakers():
    game_data = {
        "id": "test123",
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "commence_time": "2024-01-15T19:00:00Z",
        "bookmakers": [],
    }

    result = OddsParser.parse_game(game_data)

    assert result["external_id"] == "test123"
    assert result["home_moneyline"] is None
    assert result["away_moneyline"] is None
    assert result["home_spread"] is None
    assert result["total_points"] is None


def test_parse_game_missing_market():
    game_data = {
        "id": "test123",
        "home_team": "Los Angeles Lakers",
        "away_team": "Golden State Warriors",
        "commence_time": "2024-01-15T19:00:00Z",
        "bookmakers": [
            {
                "key": "betmgm",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Los Angeles Lakers", "price": -110},
                            {"name": "Golden State Warriors", "price": 120},
                        ],
                    }
                ],
            }
        ],
    }

    result = OddsParser.parse_game(game_data)

    assert result["home_moneyline"] == Decimal("-110")
    assert result["away_moneyline"] == Decimal("120")
    assert result["home_spread"] is None
    assert result["total_points"] is None


def test_parse_timestamp():
    game_data = {
        "id": "test123",
        "home_team": "Lakers",
        "away_team": "Warriors",
        "commence_time": "2024-01-15T19:30:00Z",
        "bookmakers": [],
    }

    result = OddsParser.parse_game(game_data)

    assert result["commence_time"].year == 2024
    assert result["commence_time"].month == 1
    assert result["commence_time"].day == 15
    assert result["commence_time"].hour == 19
    assert result["commence_time"].minute == 30
    assert result["commence_time"].tzinfo is None
