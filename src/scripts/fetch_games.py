"""Script to fetch games from The Odds API and populate the database."""

from src.database import get_database
from src.services.game_sync_service import GameSyncService
from src.config import config


def main():
    print("Fetching NBA games from The Odds API...")

    db = get_database(config.DATABASE_URL)

    with db.get_session() as session:
        sync_service = GameSyncService(session)

        try:
            result = sync_service.sync_games()

            print(f"\n✓ Sync complete!")
            print(f"  Created: {result['created']} games")
            print(f"  Updated: {result['updated']} games")
            print(f"  Total from API: {result['total']} games")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            raise


if __name__ == "__main__":
    main()
