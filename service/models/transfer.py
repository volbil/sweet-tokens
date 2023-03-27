from .base import Base, NativeDatetimeField
from tortoise import fields

class Transfer(Base):
    value = fields.DecimalField(max_digits=28, decimal_places=8)
    category = fields.CharField(index=True, max_length=32)
    txid = fields.CharField(index=True, max_length=64)
    has_lock = fields.BooleanField()
    created = NativeDatetimeField()
    version = fields.IntField()

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        "models.Block", related_name="transfers",
        on_delete=fields.CASCADE
    )

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="transfers",
        on_delete=fields.CASCADE
    )

    sender: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="transfers_send", null=True
    )

    receiver: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="transfers_receive", null=True
    )

    index = fields.ReverseRelation["Index"]
    locks = fields.ReverseRelation["Lock"]

    class Meta:
        table = "service_transfers"
