"""Logic for determining bet outcomes based on game results."""

from decimal import Decimal
from betting.models import BetType, BetSelection, BetStatus


def determine_moneyline_outcome(
    selection: BetSelection, home_score: int, away_score: int
) -> BetStatus:
    """
    Determine outcome of a moneyline bet.

    Args:
        selection: HOME or AWAY
        home_score: Final home team score
        away_score: Final away team score

    Returns:
        BetStatus (WON or LOST)
    """
    if selection == BetSelection.HOME:
        return BetStatus.WON if home_score > away_score else BetStatus.LOST
    else:  # AWAY
        return BetStatus.WON if away_score > home_score else BetStatus.LOST


def determine_spread_outcome(
    selection: BetSelection, spread: Decimal, home_score: int, away_score: int
) -> BetStatus:
    """
    Determine outcome of a spread bet.

    Spread betting: The favorite gives points, the underdog receives points.
    - Home spread of -5.5 means home team must win by more than 5.5 points
    - Away spread of +5.5 means away team can lose by up to 5.5 points and still cover

    Args:
        selection: HOME or AWAY
        spread: The spread line (e.g., -5.5 for home favorite, +5.5 for away underdog)
        home_score: Final home team score
        away_score: Final away team score

    Returns:
        BetStatus (WON, LOST, or PUSH)
    """
    # Apply the spread to the selected team's score
    if selection == BetSelection.HOME:
        adjusted_home = Decimal(str(home_score)) + spread
        if adjusted_home > away_score:
            return BetStatus.WON
        elif adjusted_home == away_score:
            return BetStatus.PUSH
        else:
            return BetStatus.LOST
    else:  # AWAY
        adjusted_away = Decimal(str(away_score)) + spread
        if adjusted_away > home_score:
            return BetStatus.WON
        elif adjusted_away == home_score:
            return BetStatus.PUSH
        else:
            return BetStatus.LOST


def determine_over_under_outcome(
    selection: BetSelection, total_line: Decimal, home_score: int, away_score: int
) -> BetStatus:
    """
    Determine outcome of an over/under (totals) bet.

    Args:
        selection: OVER or UNDER
        total_line: The total points line (e.g., 215.5)
        home_score: Final home team score
        away_score: Final away team score

    Returns:
        BetStatus (WON, LOST, or PUSH)
    """
    total_points = Decimal(str(home_score + away_score))

    if selection == BetSelection.OVER:
        if total_points > total_line:
            return BetStatus.WON
        elif total_points == total_line:
            return BetStatus.PUSH
        else:
            return BetStatus.LOST
    else:  # UNDER
        if total_points < total_line:
            return BetStatus.WON
        elif total_points == total_line:
            return BetStatus.PUSH
        else:
            return BetStatus.LOST


def settle_bet(
    bet_type: BetType,
    selection: BetSelection,
    home_score: int,
    away_score: int,
    spread: Decimal = None,
    total_line: Decimal = None,
) -> BetStatus:
    """
    Determine the outcome of a bet based on game results.

    Args:
        bet_type: Type of bet (MONEYLINE, SPREAD, OVER_UNDER)
        selection: User's selection (HOME, AWAY, OVER, UNDER)
        home_score: Final home team score
        away_score: Final away team score
        spread: Spread line (required for SPREAD bets)
        total_line: Total points line (required for OVER_UNDER bets)

    Returns:
        BetStatus indicating the outcome

    Raises:
        ValueError: If required parameters are missing
    """
    if bet_type == BetType.MONEYLINE:
        return determine_moneyline_outcome(selection, home_score, away_score)

    elif bet_type == BetType.SPREAD:
        if spread is None:
            raise ValueError("Spread is required for SPREAD bets")
        return determine_spread_outcome(selection, spread, home_score, away_score)

    elif bet_type == BetType.OVER_UNDER:
        if total_line is None:
            raise ValueError("Total line is required for OVER_UNDER bets")
        return determine_over_under_outcome(
            selection, total_line, home_score, away_score
        )

    else:
        raise ValueError(f"Unknown bet type: {bet_type}")
