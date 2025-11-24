"""Service for placing and managing bets."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models import User, Game, Bet, BetType, BetSelection, BetStatus, GameStatus
from src.services.odds_calculator import calculate_payout
from src.repositories import UserRepository, GameRepository, BetRepository


class BettingError(Exception):
    """Base exception for betting errors."""
    pass


class InsufficientBalanceError(BettingError):
    """Raised when user has insufficient balance."""
    pass


class InvalidBetError(BettingError):
    """Raised when bet parameters are invalid."""
    pass


class BettingService:
    """Service for placing and managing bets."""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.game_repo = GameRepository(session)
        self.bet_repo = BetRepository(session)

    def place_bet(
        self,
        user_id: UUID,
        game_id: UUID,
        bet_type: BetType,
        selection: BetSelection,
        stake: Decimal,
    ) -> Bet:
        """
        Place a bet for a user on a game.

        Args:
            user_id: User's UUID
            game_id: Game's UUID
            bet_type: Type of bet (MONEYLINE, SPREAD, OVER_UNDER)
            selection: User's selection (HOME, AWAY, OVER, UNDER)
            stake: Amount to wager

        Returns:
            Created Bet object

        Raises:
            InsufficientBalanceError: If user doesn't have enough balance
            InvalidBetError: If bet parameters are invalid
        """
        if stake <= 0:
            raise InvalidBetError("Stake must be greater than 0")

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise InvalidBetError("User not found")

        if user.balance < stake:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: ${user.balance}, Required: ${stake}"
            )

        game = self.game_repo.find_by_id(game_id)
        if not game:
            raise InvalidBetError("Game not found")

        if game.status != GameStatus.UPCOMING:
            raise InvalidBetError("Cannot bet on a game that has already started or completed")

        if game.commence_time <= datetime.now():
            raise InvalidBetError("Game has already started")

        # Get odds for the bet type and selection
        odds = self._get_odds(game, bet_type, selection)
        if odds is None:
            raise InvalidBetError(f"Odds not available for {bet_type.value} - {selection}")

        # Calculate potential payout
        potential_payout = calculate_payout(stake, odds)

        # Create bet
        bet = Bet(
            user_id=user_id,
            game_id=game_id,
            bet_type=bet_type,
            selection=selection,
            odds=odds,
            stake=stake,
        potential_payout=potential_payout,
            status=BetStatus.PENDING,
        )

        # Deduct stake from user balance
        user.balance -= stake

        # Save to database
        self.bet_repo.save(bet)
        self.bet_repo.commit()
        self.session.refresh(bet)

        return bet

    def _get_odds(self, game: Game, bet_type: BetType, selection: BetSelection) -> Optional[Decimal]:
        """
        Get odds for a specific bet type and selection.

        Args:
            game: Game object
            bet_type: Type of bet
            selection: User's selection

        Returns:
            Odds in American format, or None if not available
        """
        if bet_type == BetType.MONEYLINE:
            if selection == BetSelection.HOME:
                return game.home_moneyline
            elif selection == BetSelection.AWAY:
                return game.away_moneyline

        elif bet_type == BetType.SPREAD:
            if selection == BetSelection.HOME:
                return game.home_spread_odds
            elif selection == BetSelection.AWAY:
                return game.away_spread_odds

        elif bet_type == BetType.OVER_UNDER:
            if selection == BetSelection.OVER:
                return game.over_odds
            elif selection == BetSelection.UNDER:
                return game.under_odds

        return None

    def get_user_balance(self, user_id: UUID) -> Decimal:
        """Get current user balance."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise InvalidBetError("User not found")
        return user.balance

    def get_pending_bets(self, user_id: UUID) -> list[Bet]:
        """Get all pending bets for a user."""
        return self.bet_repo.find_pending_bets_by_user(user_id)

    def get_bet_history(self, user_id: UUID, limit: int = 50) -> list[Bet]:
        """Get bet history for a user."""
        return self.bet_repo.find_bet_history_by_user(user_id, limit)
