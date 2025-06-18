from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Numeric, String
from datetime import datetime
from .base import Base


class Token(Base):
    __tablename__ = "service_tokens"

    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    supply: Mapped[Numeric] = mapped_column(Numeric(28, 8))
    reissuable: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime]
    decimals: Mapped[int]

    balances: Mapped[list["Balance"]] = relationship(
        back_populates="token", viewonly=True
    )

    # transfers = fields.ReverseRelation["Transfer"]
    # index = fields.ReverseRelation["Index"]
    # locks = fields.ReverseRelation["Lock"]
