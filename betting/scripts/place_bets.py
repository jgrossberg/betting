"""Interactive CLI for placing bets on games."""

from decimal import Decimal
from betting.database import get_database
from betting.config import config
from betting.models import User, Game, GameStatus, BetType, BetSelection
from betting.services import BettingService, InsufficientBalanceError, InvalidBetError
from betting.repositories import UserRepository, GameRepository


def display_game(game: Game, index: int):
    """Display a single game with odds."""
    print(f"\n{'='*60}")
    print(f"Game {index + 1}: {game.away_team} @ {game.home_team}")
    print(f"Time: {game.commence_time}")
    print(f"{'='*60}")

    if game.home_moneyline and game.away_moneyline:
        print(f"\nMoneyline:")
        print(f"  Home ({game.home_team}): {game.home_moneyline}")
        print(f"  Away ({game.away_team}): {game.away_moneyline}")

    if game.home_spread and game.away_spread:
        print(f"\nSpread:")
        print(f"  Home {game.home_spread} ({game.home_spread_odds})")
        print(f"  Away {game.away_spread} ({game.away_spread_odds})")

    if game.total_points:
        print(f"\nTotals (O/U {game.total_points}):")
        print(f"  Over: {game.over_odds}")
        print(f"  Under: {game.under_odds}")


def prompt_for_bet(game: Game, user_id, service: BettingService):
    """Prompt user to place a bet on a game."""
    print(f"\n{'─'*60}")

    bet_choice = input("\nPlace a bet on this game? (y/n/skip): ").lower().strip()

    if bet_choice not in ["y", "yes"]:
        print("Skipping...")
        return

    print("\nBet Type:")
    print("  1. Moneyline")
    print("  2. Spread")
    print("  3. Over/Under")

    bet_type_choice = input("Choose (1/2/3): ").strip()

    bet_type_map = {
        "1": BetType.MONEYLINE,
        "2": BetType.SPREAD,
        "3": BetType.OVER_UNDER,
    }

    if bet_type_choice not in bet_type_map:
        print("Invalid choice, skipping...")
        return

    bet_type = bet_type_map[bet_type_choice]

    if bet_type == BetType.MONEYLINE:
        selection_choice = (
            input(f"Pick Home ({game.home_team}) or Away ({game.away_team})? (h/a): ")
            .lower()
            .strip()
        )
        selection = BetSelection.HOME if selection_choice == "h" else BetSelection.AWAY
    elif bet_type == BetType.SPREAD:
        selection_choice = (
            input(f"Pick Home {game.home_spread} or Away {game.away_spread}? (h/a): ")
            .lower()
            .strip()
        )
        selection = BetSelection.HOME if selection_choice == "h" else BetSelection.AWAY
    else:  # OVER_UNDER
        selection_choice = (
            input(f"Pick Over or Under {game.total_points}? (o/u): ").lower().strip()
        )
        selection = BetSelection.OVER if selection_choice == "o" else BetSelection.UNDER

    stake_input = input("Enter stake amount: $").strip()
    try:
        stake = Decimal(stake_input)
    except:
        print("Invalid stake amount, skipping...")
        return

    try:
        bet = service.place_bet(user_id, game.id, bet_type, selection, stake)
        print(f"\n✓ Bet placed successfully!")
        print(f"  Stake: ${bet.stake}")
        print(f"  Potential payout: ${bet.potential_payout}")
    except (InsufficientBalanceError, InvalidBetError) as e:
        print(f"\n✗ Error: {str(e)}")


def main():
    print("=" * 60)
    print("NBA BETTING - PLACE BETS")
    print("=" * 60)

    db = get_database(config.DATABASE_URL)

    with db.get_session() as session:
        service = BettingService(session)
        user_repo = UserRepository(session)
        game_repo = GameRepository(session)

        user = user_repo.find_by_username("default")
        if not user:
            print("Error: Default user not found. Run init_db.py first.")
            return

        print(f"\nCurrent balance: ${user.balance}")

        games = game_repo.find_by_status(GameStatus.UPCOMING)

        if not games:
            print("\nNo upcoming games found. Run fetch_games.py first.")
            return

        print(f"\nFound {len(games)} upcoming games\n")

        for i, game in enumerate(games):
            display_game(game, i)
            prompt_for_bet(game, user.id, service)

            session.refresh(user)
            print(f"\nRemaining balance: ${user.balance}")

        print("\n" + "=" * 60)
        print("Done placing bets!")
        print("=" * 60)


if __name__ == "__main__":
    main()
