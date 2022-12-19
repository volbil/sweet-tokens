from tortoise import fields
from .base import Base

class Address(Base):
    label = fields.CharField(index=True, unique=True, max_length=64)
    banned = fields.BooleanField(default=False)

    transfers_receive = fields.ReverseRelation["Transfer"]
    transfers_send = fields.ReverseRelation["Transfer"]
    owned_tokens = fields.ReverseRelation["Token"]
    balances = fields.ReverseRelation["Balance"]

    class Meta:
        table = "service_addresses"
