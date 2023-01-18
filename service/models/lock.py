from tortoise import fields
from .base import Base

class Lock(Base):
    value = fields.DecimalField(max_digits=28, decimal_places=8, default=0)
    unlock_height = fields.IntField()

    transfer: fields.ForeignKeyRelation["Transfer"] = fields.ForeignKeyField(
        "models.Transfer", related_name="locks",
        on_delete=fields.CASCADE
    )

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="locks",
        on_delete=fields.CASCADE
    )

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="locks",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "service_locks"
