import argparse
from betting.database import get_database
from betting.config import config
from betting.services import GameScoringService, BetSettlementService
from betting.models import BetStatus


def main():
    parser = argparse.ArgumentParser(
        description="Settle pending bets for completed games"
    )

    print("=" * 60)

    print("NBA BETTING - SCORE GAMES")
    print("=" * 60)

    db = get_database(config.DATABASE_URL)

    with db.get_session() as session:
        try:
            print("\nUpdating completed games scores")
            update_service = GameScoringService(session)
            updated_games = update_service.update_completed_games(days_from=2)

            if not updated_games:
                print("No games with pending bets were updated.")
                return

            print(f"Updated {len(updated_games)} games")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            raise


if __name__ == "__main__":
    main()
