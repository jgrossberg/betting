"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.models.base import Base


class Database:
    """Database connection manager."""

    def __init__(self, db_url: str = "sqlite:///betting.db"):
        """
        Initialize database connection.

        Args:
            db_url: SQLAlchemy database URL. Defaults to SQLite file.
        """
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Yields:
            SQLAlchemy session object.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
_db_instance = None


def get_database(db_url: str = "sqlite:///betting.db") -> Database:
    """
    Get or create the global database instance.

    Args:
        db_url: SQLAlchemy database URL.

    Returns:
        Database instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_url)
    return _db_instance


def init_database(db_url: str = "sqlite:///betting.db"):
    """
    Initialize the database and create all tables.

    Args:
        db_url: SQLAlchemy database URL.
    """
    db = get_database(db_url)
    db.create_tables()
    print(f"Database initialized at {db_url}")
