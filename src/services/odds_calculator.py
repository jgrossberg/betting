"""Odds calculation utilities for American odds format."""
from decimal import Decimal


def american_to_decimal_odds(american_odds: Decimal) -> Decimal:
    if american_odds > 0:
        return (american_odds / Decimal("100")) + Decimal("1")
    else:
        return (Decimal("100") / abs(american_odds)) + Decimal("1")


def calculate_payout(stake: Decimal, american_odds: Decimal) -> Decimal:
    decimal_odds = american_to_decimal_odds(american_odds)
    return stake * decimal_odds


def calculate_winnings(stake: Decimal, american_odds: Decimal) -> Decimal:
    return calculate_payout(stake, american_odds) - stake
