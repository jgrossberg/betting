from decimal import Decimal
import pytest
from src.services.odds_calculator import (
    american_to_decimal_odds,
    calculate_payout,
    calculate_winnings,
)


def test_american_to_decimal_positive_odds():
    assert american_to_decimal_odds(Decimal("150")) == Decimal("2.5")
    assert american_to_decimal_odds(Decimal("200")) == Decimal("3")
    assert american_to_decimal_odds(Decimal("100")) == Decimal("2")


def test_american_to_decimal_negative_odds():
    assert american_to_decimal_odds(Decimal("-110")) == Decimal(
        "1.909090909090909090909090909"
    )
    assert american_to_decimal_odds(Decimal("-200")) == Decimal("1.5")
    assert american_to_decimal_odds(Decimal("-150")) == Decimal(
        "1.666666666666666666666666667"
    )


def test_calculate_payout_positive_odds():
    assert calculate_payout(Decimal("100"), Decimal("150")) == Decimal("250")
    assert calculate_payout(Decimal("50"), Decimal("200")) == Decimal("150")


def test_calculate_payout_negative_odds():
    payout = calculate_payout(Decimal("110"), Decimal("-110"))
    assert payout == Decimal("210")


def test_calculate_winnings_positive_odds():
    assert calculate_winnings(Decimal("100"), Decimal("150")) == Decimal("150")
    assert calculate_winnings(Decimal("50"), Decimal("200")) == Decimal("100")


def test_calculate_winnings_negative_odds():
    winnings = calculate_winnings(Decimal("110"), Decimal("-110"))
    assert winnings == Decimal("100")
