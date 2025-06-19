from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from datetime import datetime
from .base import Base


class Index(Base):
    __tablename__ = "service_index"

    category: Mapped[str] = mapped_column(String(32), index=True)
    created: Mapped[datetime]

    transfer_id = mapped_column(
        ForeignKey("service_transfers.id", ondelete="CASCADE"), index=True
    )

    address_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    token_id = mapped_column(
        ForeignKey("service_tokens.id", ondelete="CASCADE"), index=True
    )

    transfer: Mapped["Transfer"] = relationship(foreign_keys=[transfer_id])
    address: Mapped["Address"] = relationship(foreign_keys=[address_id])
    token: Mapped["Token"] = relationship(foreign_keys=[token_id])
