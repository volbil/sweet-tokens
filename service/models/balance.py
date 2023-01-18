from tortoise import fields
from .base import Base

class Balance(Base):
    received = fields.DecimalField(max_digits=28, decimal_places=8, default=0)
    locked = fields.DecimalField(max_digits=28, decimal_places=8, default=0)
    value = fields.DecimalField(max_digits=28, decimal_places=8, default=0)
    sent = fields.DecimalField(max_digits=28, decimal_places=8, default=0)

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="balances",
        on_delete=fields.CASCADE
    )

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="balances",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "service_balances"
