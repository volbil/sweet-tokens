from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime
from .base import Base


class Index(Base):
    __tablename__ = "service_index"

    category: Mapped[str] = mapped_column(String(32), index=True)
    created: Mapped[datetime]

    # address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
    #     "models.Address", related_name="index"
    # )

    # transfer: fields.ForeignKeyRelation["Transfer"] = fields.ForeignKeyField(
    #     "models.Transfer", related_name="index",
    #     on_delete=fields.CASCADE
    # )

    # token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
    #     "models.Token", related_name="index",
    #     on_delete=fields.CASCADE
    # )
