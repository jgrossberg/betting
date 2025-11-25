from datetime import datetime
from typing import List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from src.models import Bet, BetStatus, BetType, Game, User
from .bet_settlement import settle_bet
from src.repositories import BetRepository, UserRepository


class BetSettlementService:
    def __init__(self, session: Session):
        self.session = session
        self.bet_repo = BetRepository(session)
        self.user_repo = UserRepository(session)

    def settle_bets_for_games(self, completed_games: List[Game]) -> List[Bet]:
        settled_bets = []

        for game in completed_games:
            game_bets = self.bet_repo.find_pending_bets_by_game(game.id)

            for bet in game_bets:
                outcome = self._determine_bet_outcome(bet, game)
                self._process_bet_outcome(bet, outcome)
                settled_bets.append(bet)

        self.bet_repo.commit()
        return settled_bets

    def preview_settlements(self, completed_games: List[Game]) -> Dict[str, Any]:
        preview_data = {
            "bets": [],
            "won_count": 0,
            "lost_count": 0,
            "push_count": 0,
            "total_payout": Decimal("0"),
        }

        for game in completed_games:
            game_bets = self.bet_repo.find_pending_bets_by_game(game.id)

            for bet in game_bets:
                outcome = self._determine_bet_outcome(bet, game)
                user = self.user_repo.find_by_id(bet.user_id)

                payout = Decimal("0")
                if outcome == BetStatus.WON:
                    payout = bet.potential_payout
                    preview_data["won_count"] += 1
                    preview_data["total_payout"] += payout
                elif outcome == BetStatus.LOST:
                    preview_data["lost_count"] += 1
                elif outcome == BetStatus.PUSH:
                    payout = bet.stake
                    preview_data["push_count"] += 1
                    preview_data["total_payout"] += payout

                preview_data["bets"].append(
                    {
                        "bet": bet,
                        "game": game,
                        "outcome": outcome,
                        "payout": payout,
                        "user": user,
                    }
                )

        return preview_data

    def _determine_bet_outcome(self, bet: Bet, game: Game) -> BetStatus:
        if bet.bet_type == BetType.MONEYLINE:
            return settle_bet(
                bet.bet_type, bet.selection, game.home_score, game.away_score
            )

        elif bet.bet_type == BetType.SPREAD:
            spread = (
                game.home_spread if bet.selection.value == "home" else game.away_spread
            )
            return settle_bet(
                bet.bet_type,
                bet.selection,
                game.home_score,
                game.away_score,
                spread=spread,
            )

        elif bet.bet_type == BetType.OVER_UNDER:
            return settle_bet(
                bet.bet_type,
                bet.selection,
                game.home_score,
                game.away_score,
                total_line=game.total_points,
            )

    def _process_bet_outcome(self, bet: Bet, outcome: BetStatus):
        bet.status = outcome
        bet.settled_at = datetime.now()

        user = self.user_repo.find_by_id(bet.user_id)

        if outcome == BetStatus.WON:
            user.balance += bet.potential_payout
        elif outcome == BetStatus.PUSH:
            user.balance += bet.stake
