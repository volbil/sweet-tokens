from tortoise import fields
from .base import Base

class Address(Base):
    raw_address = fields.CharField(unique=True, max_length=40)
    nonce = fields.IntField(default=0)

    banned = fields.BooleanField(default=False)

    balances = fields.ReverseRelation["Balance"]

    transfers_send = fields.ReverseRelation["Transfer"]
    transfers_receive = fields.ReverseRelation["Transfer"]

    class Meta:
        table = "service_addresses"
