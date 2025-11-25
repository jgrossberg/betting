from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.models import Game, GameStatus
from src.repositories import GameRepository
from src.the_odds_api.client import TheOddsApiClient


class GameScoringService:
    def __init__(self, session: Session, api_client: TheOddsApiClient = None):
        self.session = session
        self.game_repo = GameRepository(session)
        self.api_client = api_client or TheOddsApiClient()

    def update_completed_games(self, days_from: int = 1) -> List[Game]:
        pending_games = self.game_repo.find_unfinished_games()

        if not pending_games:
            return []

        score_data_list = self.api_client.get_nba_scores(days_from=days_from)

        if not score_data_list:
            return []

        return self._update_games_from_scores(score_data_list)

    def _update_games_from_scores(self, score_data_list: List[Dict[str, Any]]) -> List[Game]:
        updated_games = []

        for score_data in score_data_list:
            game = self.game_repo.find_by_external_id(score_data["external_id"])

            if not game:
                continue

            if game.status == GameStatus.COMPLETED:
                continue

            game.home_score = score_data["home_score"]
            game.away_score = score_data["away_score"]
            game.status = GameStatus.COMPLETED

            updated_games.append(game)

        self.game_repo.commit()
        return updated_games
