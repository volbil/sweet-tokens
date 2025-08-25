from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String
from datetime import datetime
from decimal import Decimal
from .base import Base


class Token(Base):
    __tablename__ = "service_tokens"

    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    supply: Mapped[Decimal] = mapped_column(Numeric(28, 8))
    reissuable: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime]
    decimals: Mapped[int]
