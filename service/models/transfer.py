from tortoise import fields
from .base import Base

class Transfer(Base):
    amount = fields.DecimalField(max_digits=28, decimal_places=8)
    txid = fields.CharField(unique=True, max_length=64)

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="transfers"
    )

    sender: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="transfers_send"
    )

    receiver: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="transfers_receive"
    )

    class Meta:
        table = "service_transfers"
