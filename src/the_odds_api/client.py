from typing import List, Dict, Any
import requests
from src.config import config
from .parser import OddsParser


class OddsAPIError(Exception):
    pass


class TheOddsApiClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or config.ODDS_API_KEY
        self.base_url = base_url or config.ODDS_API_BASE_URL

        if not self.api_key:
            raise OddsAPIError("ODDS_API_KEY not configured")

    def get_nba_games(self, markets: str = "h2h,spreads,totals") -> List[Dict[str, Any]]:
        """
        Fetch NBA games and return parsed data ready for database insertion.

        Returns:
            List of game dictionaries ready for Game(**dict)
        """
        raw_data = self._fetch_nba_odds(markets)
        return [OddsParser.parse_game(game_data) for game_data in raw_data]

    def get_nba_scores(self, days_from: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch NBA game scores and return parsed data ready for database update.

        Args:
            days_from: Number of days from now to fetch scores for

        Returns:
            List of score dictionaries with external_id, home_score, away_score, completed
        """
        raw_data = self._fetch_nba_scores(days_from)
        return [OddsParser.parse_scores(score_data) for score_data in raw_data if score_data.get("completed")]

    def _fetch_nba_odds(self, markets: str = "h2h,spreads,totals") -> List[Dict[str, Any]]:
        """Internal method to fetch raw odds data from API."""
        url = f"{self.base_url}/sports/upcoming/odds"

        params = {
            "apiKey": self.api_key,
            "sport": config.ODDS_API_SPORT,
            "regions": "us",
            "markets": markets,
            "oddsFormat": "american",
            "bookmakers": "betmgm",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise OddsAPIError(f"Failed to fetch odds: {str(e)}")

    def _fetch_nba_scores(self, days_from: int = 1) -> List[Dict[str, Any]]:
        """Internal method to fetch game scores from API."""
        url = f"{self.base_url}/sports/{config.ODDS_API_SPORT}/scores"

        params = {
            "apiKey": self.api_key,
            "daysFrom": days_from,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise OddsAPIError(f"Failed to fetch scores: {str(e)}")

    def check_usage(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/sports",
            params={"apiKey": self.api_key},
            timeout=10
        )

        return {
            "requests_remaining": response.headers.get("x-requests-remaining"),
            "requests_used": response.headers.get("x-requests-used"),
        }
