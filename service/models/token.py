from tortoise import fields
from .base import Base

class Token(Base):
    name = fields.CharField(unique=True, max_length=24)
    ticker = fields.CharField(unique=True, max_length=8)
    supply = fields.DecimalField(max_digits=28, decimal_places=8)
    reissuable = fields.BooleanField(default=False)

    balances = fields.ReverseRelation["Balance"]
    transfers = fields.ReverseRelation["Transfer"]

    class Meta:
        table = "service_tokens"
