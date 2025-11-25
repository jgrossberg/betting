from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import exists
from src.models import Game, GameStatus, Bet, BetStatus


class GameRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, game_id) -> Optional[Game]:
        return self.session.query(Game).filter_by(id=game_id).first()

    def find_by_external_id(self, external_id: str) -> Optional[Game]:
        return self.session.query(Game).filter_by(external_id=external_id).first()

    def find_by_status(self, status: GameStatus) -> List[Game]:
        return self.session.query(Game).filter_by(status=status).all()

    def find_games_with_pending_bets(self, status: GameStatus) -> List[Game]:
        return (
            self.session.query(Game)
            .filter(
                Game.status == status,
                exists().where(
                    (Bet.game_id == Game.id) & (Bet.status == BetStatus.PENDING)
                ),
            )
            .all()
        )

    def find_unfinished_games(self) -> List[Game]:
        return (
            self.session.query(Game).filter(Game.status != GameStatus.COMPLETED).all()
        )

    def save(self, game: Game) -> Game:
        self.session.add(game)
        return game

    def commit(self):
        self.session.commit()
