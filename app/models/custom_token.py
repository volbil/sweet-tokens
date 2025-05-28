from .base import Base, NativeDatetimeField
from tortoise import fields

class Token(Base):
    supply = fields.DecimalField(max_digits=28, decimal_places=8)
    ticker = fields.CharField(unique=True, max_length=32)
    reissuable = fields.BooleanField(default=False)
    type = fields.CharField(max_length=32)
    created = NativeDatetimeField()
    decimals = fields.IntField()

    transfers = fields.ReverseRelation["Transfer"]
    balances = fields.ReverseRelation["Balance"]
    index = fields.ReverseRelation["Index"]
    locks = fields.ReverseRelation["Lock"]

    class Meta:
        table = "service_tokens"
