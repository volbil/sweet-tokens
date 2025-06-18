from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime
from .base import Base


class Block(Base):
    __tablename__ = "service_blocks"

    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    height: Mapped[int] = mapped_column(index=True)
    created: Mapped[datetime]

    bans: Mapped[list["Ban"]] = relationship(
        back_populates="block", viewonly=True
    )

    unbans: Mapped[list["Unban"]] = relationship(
        back_populates="block", viewonly=True
    )

    # fee_addresses = fields.ReverseRelation["FeeAddress"]
    # transfers = fields.ReverseRelation["Transfer"]
    # costs = fields.ReverseRelation["TokenCost"]
