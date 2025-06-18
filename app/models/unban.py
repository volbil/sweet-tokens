from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base


class Unban(Base):
    __tablename__ = "service_unbans"

    txid: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    address_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    admin_id = mapped_column(
        ForeignKey("service_addresses.id", ondelete="CASCADE"), index=True
    )

    block_id = mapped_column(
        ForeignKey("service_blocks.id", ondelete="CASCADE"), index=True
    )

    address: Mapped["Address"] = relationship(
        back_populates="address_unban", foreign_keys=[address_id]
    )

    admin: Mapped["Address"] = relationship(
        back_populates="admin_unban", foreign_keys=[admin_id]
    )

    block: Mapped["Block"] = relationship(
        back_populates="unbans", foreign_keys=[block_id]
    )
