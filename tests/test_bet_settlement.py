from decimal import Decimal
import pytest
from src.models import BetType, BetSelection, BetStatus
from src.services.bet_settlement import (
    determine_moneyline_outcome,
    determine_spread_outcome,
    determine_over_under_outcome,
    settle_bet,
)


class TestMoneyline:
    def test_home_wins(self):
        assert determine_moneyline_outcome(BetSelection.HOME, 100, 95) == BetStatus.WON

    def test_home_loses(self):
        assert determine_moneyline_outcome(BetSelection.HOME, 95, 100) == BetStatus.LOST

    def test_away_wins(self):
        assert determine_moneyline_outcome(BetSelection.AWAY, 95, 100) == BetStatus.WON

    def test_away_loses(self):
        assert determine_moneyline_outcome(BetSelection.AWAY, 100, 95) == BetStatus.LOST


class TestSpread:
    def test_home_covers_negative_spread(self):
        result = determine_spread_outcome(BetSelection.HOME, Decimal("-5.5"), 100, 90)
        assert result == BetStatus.WON

    def test_home_doesnt_cover_negative_spread(self):
        result = determine_spread_outcome(BetSelection.HOME, Decimal("-5.5"), 100, 95)
        assert result == BetStatus.LOST

    def test_away_covers_positive_spread(self):
        result = determine_spread_outcome(BetSelection.AWAY, Decimal("5.5"), 100, 95)
        assert result == BetStatus.WON

    def test_away_doesnt_cover_positive_spread(self):
        result = determine_spread_outcome(BetSelection.AWAY, Decimal("5.5"), 100, 85)
        assert result == BetStatus.LOST

    def test_push_on_whole_number_spread(self):
        result = determine_spread_outcome(BetSelection.HOME, Decimal("-5"), 100, 95)
        assert result == BetStatus.PUSH


class TestOverUnder:
    def test_over_wins(self):
        result = determine_over_under_outcome(
            BetSelection.OVER, Decimal("215.5"), 110, 108
        )
        assert result == BetStatus.WON

    def test_over_loses(self):
        result = determine_over_under_outcome(
            BetSelection.OVER, Decimal("215.5"), 105, 108
        )
        assert result == BetStatus.LOST

    def test_under_wins(self):
        result = determine_over_under_outcome(
            BetSelection.UNDER, Decimal("215.5"), 105, 108
        )
        assert result == BetStatus.WON

    def test_under_loses(self):
        result = determine_over_under_outcome(
            BetSelection.UNDER, Decimal("215.5"), 110, 108
        )
        assert result == BetStatus.LOST

    def test_push_on_exact_total(self):
        result = determine_over_under_outcome(
            BetSelection.OVER, Decimal("216"), 110, 106
        )
        assert result == BetStatus.PUSH


class TestSettleBet:
    def test_settle_moneyline(self):
        result = settle_bet(BetType.MONEYLINE, BetSelection.HOME, 100, 95)
        assert result == BetStatus.WON

    def test_settle_spread(self):
        result = settle_bet(
            BetType.SPREAD, BetSelection.HOME, 100, 90, spread=Decimal("-5.5")
        )
        assert result == BetStatus.WON

    def test_settle_over_under(self):
        result = settle_bet(
            BetType.OVER_UNDER, BetSelection.OVER, 110, 108, total_line=Decimal("215.5")
        )
        assert result == BetStatus.WON

    def test_missing_spread_raises_error(self):
        with pytest.raises(ValueError, match="Spread is required"):
            settle_bet(BetType.SPREAD, BetSelection.HOME, 100, 90)

    def test_missing_total_line_raises_error(self):
        with pytest.raises(ValueError, match="Total line is required"):
            settle_bet(BetType.OVER_UNDER, BetSelection.OVER, 110, 108)
