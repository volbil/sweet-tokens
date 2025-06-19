from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Numeric, String
from sqlalchemy import ForeignKey
from .base import Base


class FeeAddress(Base):
    __tablename__ = "service_fee_addresses"

    label: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    height: Mapped[int] = mapped_column(index=True)

    admin_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    block_id = mapped_column(
        ForeignKey("service_blocks.id", ondelete="CASCADE"), index=True
    )

    admin: Mapped["Address"] = relationship(foreign_keys=[admin_id])
    block: Mapped["Block"] = relationship(foreign_keys=[block_id])


class TokenCost(Base):
    __tablename__ = "service_costs"

    action: Mapped[str] = mapped_column(String(32), index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    value: Mapped[Numeric] = mapped_column(Numeric(28, 8))
    height: Mapped[int] = mapped_column(index=True)

    admin_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    block_id = mapped_column(
        ForeignKey("service_blocks.id", ondelete="CASCADE"), index=True
    )

    admin: Mapped["Address"] = relationship(foreign_keys=[admin_id])
    block: Mapped["Block"] = relationship(foreign_keys=[block_id])
