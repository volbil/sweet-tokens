from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String
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

    # block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
    #     "models.Block", related_name="transfers",
    #     on_delete=fields.CASCADE
    # )

    # token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
    #     "models.Token", related_name="transfers",
    #     on_delete=fields.CASCADE
    # )

    # sender: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="transfers_send", null=True
    # )

    # receiver: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="transfers_receive", null=True
    # )

    # index = fields.ReverseRelation["Index"]
    # locks = fields.ReverseRelation["Lock"]
