from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.models.base import Base


class Database:

    def __init__(self, db_url: str = "sqlite:///betting.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


_db_instance = None


def get_database(db_url: str = "sqlite:///betting.db") -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_url)
    return _db_instance


def init_database(db_url: str = "sqlite:///betting.db"):
    db = get_database(db_url)
    db.create_tables()
    print(f"Database initialized at {db_url}")
