from tortoise import fields
from .base import Base

class Block(Base):
    hash = fields.CharField(max_length=64, index=True)
    height = fields.IntField()

    transfers = fields.ReverseRelation["Transfer"]

    class Meta:
        table = "service_blocks"
