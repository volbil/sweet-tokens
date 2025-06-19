from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from .base import Base


class Lock(Base):
    __tablename__ = "service_locks"

    value: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)
    unlock_height: Mapped[int] = mapped_column(index=True)

    address_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    transfer_id = mapped_column(
        ForeignKey("service_transfers.id", ondelete="CASCADE"), index=True
    )

    token_id = mapped_column(
        ForeignKey("service_tokens.id", ondelete="CASCADE"), index=True
    )

    transfer: Mapped["Transfer"] = relationship(foreign_keys=[transfer_id])
    address: Mapped["Address"] = relationship(foreign_keys=[address_id])
    token: Mapped["Token"] = relationship(foreign_keys=[token_id])
