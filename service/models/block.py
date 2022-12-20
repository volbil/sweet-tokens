from .base import Base, NativeDatetimeField
from tortoise import fields

class Block(Base):
    hash = fields.CharField(max_length=64, index=True)
    created = NativeDatetimeField()
    height = fields.IntField()

    transfers = fields.ReverseRelation["Transfer"]
    unbans = fields.ReverseRelation["Unban"]
    bans = fields.ReverseRelation["Ban"]

    class Meta:
        table = "service_blocks"
