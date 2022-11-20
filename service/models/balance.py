from tortoise import fields
from .base import Base

class Balance(Base):
    amount = fields.DecimalField(max_digits=28, decimal_places=8, default=0)

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="balances"
    )

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="balances"
    )

    class Meta:
        table = "service_balances"
