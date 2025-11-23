from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import String, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("1000.00")
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', balance={self.balance})>"
