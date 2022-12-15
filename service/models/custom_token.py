from tortoise import fields
from .base import Base

class Token(Base):
    supply = fields.DecimalField(max_digits=28, decimal_places=8)
    ticker = fields.CharField(unique=True, max_length=8)
    reissuable = fields.BooleanField(default=False)
    decimals = fields.IntField()

    transfers = fields.ReverseRelation["Transfer"]
    balances = fields.ReverseRelation["Balance"]

    class Meta:
        table = "service_tokens"
