from decimal import Decimal
import pytest
from unittest.mock import Mock
from pytest_mock import MockFixture
import requests
from src.the_odds_api.client import TheOddsApiClient, OddsAPIError


@pytest.fixture
def mock_api_response():
    return [
        {
            "id": "game1",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "commence_time": "2024-01-15T19:00:00Z",
            "bookmakers": [
                {
                    "key": "betmgm",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Lakers", "price": -110},
                                {"name": "Warriors", "price": 100},
                            ],
                        }
                    ],
                }
            ],
        }
    ]


def test_get_nba_games_success(mocker: MockFixture, mock_api_response):
    mock_response = Mock()
    mock_response.json.return_value = mock_api_response
    mock_response.raise_for_status = Mock()
    mock_get = mocker.patch(
        "src.the_odds_api.client.requests.get", return_value=mock_response
    )

    client = TheOddsApiClient(api_key="test_key")
    games = client.get_nba_games()

    assert len(games) == 1
    assert games[0]["external_id"] == "game1"
    assert games[0]["home_team"] == "Lakers"
    assert games[0]["away_team"] == "Warriors"
    assert games[0]["home_moneyline"] == Decimal("-110")
    assert games[0]["away_moneyline"] == Decimal("100")

    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "oddsFormat" in call_args.kwargs["params"]
    assert call_args.kwargs["params"]["oddsFormat"] == "american"
    assert call_args.kwargs["params"]["bookmakers"] == "betmgm"


def test_get_nba_games_api_error(mocker: MockFixture):
    mocker.patch(
        "src.the_odds_api.client.requests.get",
        side_effect=requests.RequestException("API Down"),
    )

    client = TheOddsApiClient(api_key="test_key")

    with pytest.raises(OddsAPIError, match="Failed to fetch odds"):
        client.get_nba_games()


def test_client_missing_api_key(mocker: MockFixture):
    mock_config = mocker.patch("src.the_odds_api.client.config")
    mock_config.ODDS_API_KEY = ""
    mock_config.ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

    with pytest.raises(OddsAPIError, match="ODDS_API_KEY not configured"):
        TheOddsApiClient(api_key=None)


def test_check_usage(mocker: MockFixture):
    mock_response = Mock()
    mock_response.headers = {"x-requests-remaining": "450", "x-requests-used": "50"}
    mocker.patch("src.the_odds_api.client.requests.get", return_value=mock_response)

    client = TheOddsApiClient(api_key="test_key")
    usage = client.check_usage()

    assert usage["requests_remaining"] == "450"
    assert usage["requests_used"] == "50"
