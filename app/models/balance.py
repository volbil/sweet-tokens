from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from .base import Base


class Balance(Base):
    __tablename__ = "service_balances"

    received: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)
    locked: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)
    value: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)
    sent: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)

    address_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    token_id = mapped_column(
        ForeignKey("service_tokens.id", ondelete="CASCADE"), index=True
    )

    address: Mapped["Address"] = relationship(foreign_keys=[address_id])
    token: Mapped["Token"] = relationship(foreign_keys=[token_id])
