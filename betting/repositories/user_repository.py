from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from betting.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def find_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

    def create(self, username: str, balance: Decimal) -> User:
        user = User(username=username, balance=balance)
        self.session.add(user)
        self.session.flush()
        return user

    def save(self, user: User) -> User:
        self.session.add(user)
        return user

    def commit(self):
        self.session.commit()
