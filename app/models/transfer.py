from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Numeric, String
from sqlalchemy import ForeignKey
from datetime import datetime
from .base import Base


class Transfer(Base):
    __tablename__ = "service_transfers"

    category: Mapped[str] = mapped_column(String(32), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[Numeric] = mapped_column(Numeric(28, 8))
    created: Mapped[datetime]
    has_lock: Mapped[bool]
    version: Mapped[int]

    block_id = mapped_column(
        ForeignKey("service_blocks.id", ondelete="CASCADE"), index=True
    )

    token_id = mapped_column(
        ForeignKey("service_tokens.id", ondelete="CASCADE"), index=True
    )

    receiver_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    sender_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    block: Mapped["Block"] = relationship(foreign_keys=[block_id])
    token: Mapped["Token"] = relationship(foreign_keys=[token_id])
    receiver: Mapped["Address"] = relationship(foreign_keys=[sender_id])
    sender: Mapped["Address"] = relationship(foreign_keys=[sender_id])
