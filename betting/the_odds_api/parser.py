from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from betting.models import GameStatus


class OddsParser:
    @staticmethod
    def parse_game(game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a game from The Odds API response into our Game model format.

        The Odds API response structure:
        {
            "id": "abc123",
            "sport_key": "basketball_nba",
            "commence_time": "2024-01-15T19:00:00Z",
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "bookmakers": [
                {
                    "key": "fanduel",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -110},
                                {"name": "Golden State Warriors", "price": 120}
                            ]
                        },
                        {
                            "key": "spreads",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": -110, "point": -5.5},
                                {"name": "Golden State Warriors", "price": -110, "point": 5.5}
                            ]
                        },
                        {
                            "key": "totals",
                            "outcomes": [
                                {"name": "Over", "price": -110, "point": 215.5},
                                {"name": "Under", "price": -110, "point": 215.5}
                            ]
                        }
                    ]
                }
            ]
        }
        """
        external_id = game_data["id"]
        home_team = game_data["home_team"]
        away_team = game_data["away_team"]
        commence_time = datetime.fromisoformat(
            game_data["commence_time"].replace("Z", "+00:00")
        ).replace(tzinfo=None)

        odds_data = OddsParser._extract_best_odds(game_data, home_team, away_team)

        return {
            "external_id": external_id,
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": commence_time,
            "status": GameStatus.UPCOMING,
            **odds_data,
        }

    @staticmethod
    def _extract_best_odds(
        game_data: Dict[str, Any], home_team: str, away_team: str
    ) -> Dict[str, Optional[Decimal]]:
        """Extract best odds across all bookmakers."""
        best_odds = {
            "home_moneyline": None,
            "away_moneyline": None,
            "home_spread": None,
            "home_spread_odds": None,
            "away_spread": None,
            "away_spread_odds": None,
            "total_points": None,
            "over_odds": None,
            "under_odds": None,
            "home_score": None,
            "away_score": None,
        }

        bookmakers = game_data.get("bookmakers", [])
        if not bookmakers:
            return best_odds

        bookmaker = bookmakers[0]

        for market in bookmaker.get("markets", []):
            market_key = market["key"]
            outcomes = market["outcomes"]

            if market_key == "h2h":
                for outcome in outcomes:
                    if outcome["name"] == home_team:
                        best_odds["home_moneyline"] = Decimal(str(outcome["price"]))
                    elif outcome["name"] == away_team:
                        best_odds["away_moneyline"] = Decimal(str(outcome["price"]))

            elif market_key == "spreads":
                for outcome in outcomes:
                    if outcome["name"] == home_team:
                        best_odds["home_spread"] = Decimal(str(outcome["point"]))
                        best_odds["home_spread_odds"] = Decimal(str(outcome["price"]))
                    elif outcome["name"] == away_team:
                        best_odds["away_spread"] = Decimal(str(outcome["point"]))
                        best_odds["away_spread_odds"] = Decimal(str(outcome["price"]))

            elif market_key == "totals":
                for outcome in outcomes:
                    if outcome["name"] == "Over":
                        best_odds["total_points"] = Decimal(str(outcome["point"]))
                        best_odds["over_odds"] = Decimal(str(outcome["price"]))
                    elif outcome["name"] == "Under":
                        best_odds["under_odds"] = Decimal(str(outcome["price"]))

        return best_odds

    @staticmethod
    def parse_scores(score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a completed game's scores from The Odds API response.

        Returns a dict with external_id, home_score, away_score, completed.
        """
        external_id = score_data["id"]
        home_team = score_data["home_team"]
        away_team = score_data["away_team"]

        home_score = None
        away_score = None

        for score_entry in score_data.get("scores", []):
            if score_entry["name"] == home_team:
                home_score = int(score_entry["score"])
            elif score_entry["name"] == away_team:
                away_score = int(score_entry["score"])

        return {
            "external_id": external_id,
            "home_score": home_score,
            "away_score": away_score,
            "completed": True,
        }
