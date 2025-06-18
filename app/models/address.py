from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base


class Address(Base):
    __tablename__ = "service_addresses"

    label: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    banned: Mapped[bool] = mapped_column(default=False)

    balances: Mapped[list["Balance"]] = relationship(
        back_populates="address", viewonly=True
    )

    address_ban: Mapped[list["Ban"]] = relationship(
        back_populates="address", viewonly=True
    )

    address_unban: Mapped[list["Unban"]] = relationship(
        back_populates="address", viewonly=True
    )

    admin_ban: Mapped[list["Ban"]] = relationship(
        back_populates="admin", viewonly=True
    )

    admin_unban: Mapped[list["Unban"]] = relationship(
        back_populates="admin", viewonly=True
    )

    # transfers_receive = fields.ReverseRelation["Transfer"]
    # transfers_send = fields.ReverseRelation["Transfer"]
    # owned_tokens = fields.ReverseRelation["Token"]

    # admin_fee_addresses = fields.ReverseRelation["FeeAddress"]
    # admin_costs = fields.ReverseRelation["TokenCost"]

    # index = fields.ReverseRelation["Index"]
    # locks = fields.ReverseRelation["Lock"]
