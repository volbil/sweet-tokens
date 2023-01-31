from .base import Base, NativeDatetimeField
from tortoise import fields

class Block(Base):
    hash = fields.CharField(max_length=64, index=True)
    created = NativeDatetimeField()
    height = fields.IntField()

    fee_addresses = fields.ReverseRelation["FeeAddress"]
    transfers = fields.ReverseRelation["Transfer"]
    costs = fields.ReverseRelation["TokenCost"]
    unbans = fields.ReverseRelation["Unban"]
    bans = fields.ReverseRelation["Ban"]

    class Meta:
        table = "service_blocks"
