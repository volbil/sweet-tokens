from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String
from .base import Base


class FeeAddress(Base):
    __tablename__ = "service_fee_addresses"

    label: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    height: Mapped[int] = mapped_column(index=True)

    # admin: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="admin_fee_addresses", null=True
    # )

    # block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
    #     "models.Block", related_name="fee_addresses", on_delete=fields.CASCADE
    # )


class TokenCost(Base):
    __tablename__ = "service_costs"

    action: Mapped[str] = mapped_column(String(32), index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    value: Mapped[Numeric] = mapped_column(Numeric(28, 8))
    height: Mapped[int] = mapped_column(index=True)

    # admin: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="admin_costs", null=True
    # )

    # block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
    #     "models.Block", related_name="costs", on_delete=fields.CASCADE
    # )
