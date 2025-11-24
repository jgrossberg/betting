from sqlalchemy.orm import Session
from src.models import Game
from src.the_odds_api import TheOddsApiClient
from src.repositories import GameRepository


class GameSyncService:
    def __init__(self, session: Session, api_client: TheOddsApiClient = None):
        self.session = session
        self.api_client = api_client or TheOddsApiClient()
        self.game_repo = GameRepository(session)

    def sync_games(self) -> dict:
        games = self.api_client.get_nba_games()

        created_count = 0
        updated_count = 0

        for game_data in games:
            existing_game = self.game_repo.find_by_external_id(game_data["external_id"])

            if existing_game:
                for key, value in game_data.items():
                    if key != "external_id":
                        setattr(existing_game, key, value)
                updated_count += 1
            else:
                new_game = Game(**game_data)
                self.game_repo.save(new_game)
                created_count += 1

        self.game_repo.commit()

        return {
            "created": created_count,
            "updated": updated_count,
            "total": len(games),
        }
