"""Initialize the database and create default user."""
from decimal import Decimal
from src.database import get_database
from src.models import User
from src.config import config


def init_database():
    """Initialize database tables and create default user."""
    print("Initializing database...")

    # Get database instance and create tables
    db = get_database(config.DATABASE_URL)
    db.create_tables()
    print(f"✓ Tables created at {config.DATABASE_URL}")

    # Create default user
    with db.get_session() as session:
        # Check if user already exists
        existing_user = session.query(User).filter_by(username="default").first()

        if existing_user:
            print(f"✓ Default user already exists (balance: ${existing_user.balance})")
        else:
            default_user = User(
                username="default", balance=Decimal(str(config.DEFAULT_USER_BALANCE))
            )
            session.add(default_user)
            session.commit()
            print(
                f"✓ Default user created with balance: ${config.DEFAULT_USER_BALANCE}"
            )

    print("\nDatabase initialization complete!")


if __name__ == "__main__":
    init_database()
