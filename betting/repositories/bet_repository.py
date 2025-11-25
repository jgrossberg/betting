from typing import List
from sqlalchemy.orm import Session
from betting.models import Bet, BetStatus


class BetRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_pending_bets_by_user(self, user_id) -> List[Bet]:
        return (
            self.session.query(Bet)
            .filter_by(user_id=user_id, status=BetStatus.PENDING)
            .all()
        )

    def find_all_bets_by_user(self, user_id) -> List[Bet]:
        return self.session.query(Bet).filter_by(user_id=user_id).all()

    def find_bet_history_by_user(self, user_id, limit: int = 50) -> List[Bet]:
        return (
            self.session.query(Bet)
            .filter_by(user_id=user_id)
            .order_by(Bet.created_at.desc())
            .limit(limit)
            .all()
        )

    def find_pending_bets_by_game(self, game_id) -> List[Bet]:
        return (
            self.session.query(Bet)
            .filter_by(game_id=game_id, status=BetStatus.PENDING)
            .all()
        )

    def save(self, bet: Bet) -> Bet:
        self.session.add(bet)
        return bet

    def commit(self):
        self.session.commit()
