import argparse
from src.database import get_database
from src.config import config
from src.services import GameUpdateService, BetSettlementService
from src.models import BetStatus

def main():
    parser = argparse.ArgumentParser(description="Settle pending bets for completed games")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview settlements without making any changes"
    )
    args = parser.parse_args()

    print("="*60)
    if args.dry_run:
        print("NBA BETTING - SETTLE BETS (DRY RUN)")
    else:
        print("NBA BETTING - SETTLE BETS")
    print("="*60)

    db = get_database(config.DATABASE_URL)

    with db.get_session() as session:
        try:
            print("\nChecking for games with pending bets and updating scores...")
            update_service = GameUpdateService(session)
            updated_games = update_service.update_completed_games(days_from=1)

            if not updated_games:
                print("No games with pending bets were updated.")
                return

            print(f"Updated {len(updated_games)} games")

            settlement_service = BetSettlementService(session)

            if args.dry_run:
                print("\nPreviewing settlement outcomes...")
                preview = settlement_service.preview_settlements(updated_games)

                if not preview["bets"]:
                    print("No pending bets to settle.")
                    return

                print(f"\n{'-'*60}")
                print(f"Settlement Preview ({len(preview['bets'])} bets):")
                print(f"  Won: {preview['won_count']}")
                print(f"  Lost: {preview['lost_count']}")
                print(f"  Push: {preview['push_count']}")
                print(f"  Total payout: ${preview['total_payout']}")

                print(f"\n{'='*60}")
                print("Bet Details:")
                print(f"{'='*60}")

                for item in preview["bets"]:
                    bet = item["bet"]
                    game = item["game"]
                    outcome = item["outcome"]
                    payout = item["payout"]
                    user = item["user"]

                    print(f"\n{game.away_team} @ {game.home_team}: {game.away_score} - {game.home_score}")
                    print(f"  User: {user.username} | Type: {bet.bet_type.value} | Selection: {bet.selection.value}")
                    print(f"  Stake: ${bet.stake} | Outcome: {outcome.value}")
                    if payout > 0:
                        print(f"  Payout: ${payout}")

                print(f"\n{'='*60}")
                print("DRY RUN - No changes made to database")
                print("Run without --dry-run to actually settle bets")
                print(f"{'='*60}")

            else:
                print("\nSettling pending bets...")
                settled_bets = settlement_service.settle_bets_for_games(updated_games)

                if not settled_bets:
                    print("No pending bets to settle.")
                    return

                print(f"\n{'-'*60}")
                print(f"Settled {len(settled_bets)} bets:")

                won_count = sum(1 for bet in settled_bets if bet.status == BetStatus.WON)
                lost_count = sum(1 for bet in settled_bets if bet.status == BetStatus.LOST)
                push_count = sum(1 for bet in settled_bets if bet.status == BetStatus.PUSH)

                print(f"  Won: {won_count}")
                print(f"  Lost: {lost_count}")
                print(f"  Push: {push_count}")

                print(f"\n{'='*60}")
                print("Settlement complete!")
                print(f"{'='*60}")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            raise


if __name__ == "__main__":
    main()
