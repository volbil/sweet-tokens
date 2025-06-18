from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric
from .base import Base


class Lock(Base):
    __tablename__ = "service_locks"

    value: Mapped[Numeric] = mapped_column(Numeric(28, 8), default=0)
    unlock_height: Mapped[int] = mapped_column(index=True)

    # transfer: fields.ForeignKeyRelation["Transfer"] = fields.ForeignKeyField(
    #     "models.Transfer", related_name="locks",
    #     on_delete=fields.CASCADE
    # )

    # address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="locks",
    #     on_delete=fields.CASCADE
    # )

    # token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
    #     "models.Token", related_name="locks",
    #     on_delete=fields.CASCADE
    # )
