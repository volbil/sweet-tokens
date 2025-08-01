from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Numeric, String
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from .base import Base

if TYPE_CHECKING:
    from .custom_token import Token
    from .address import Address
    from .block import Block


class Transfer(Base):
    __tablename__ = "service_transfers"

    category: Mapped[str] = mapped_column(String(32), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(28, 8))
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

    receiver: Mapped["Address"] = relationship(foreign_keys=[receiver_id])
    sender: Mapped["Address"] = relationship(foreign_keys=[sender_id])
    block: Mapped["Block"] = relationship(foreign_keys=[block_id])
    token: Mapped["Token"] = relationship(foreign_keys=[token_id])
