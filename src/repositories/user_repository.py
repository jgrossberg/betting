from typing import Optional
from sqlalchemy.orm import Session
from src.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def find_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

    def save(self, user: User) -> User:
        self.session.add(user)
        return user

    def commit(self):
        self.session.commit()
