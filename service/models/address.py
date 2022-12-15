from tortoise import fields
from .base import Base

class Address(Base):
    raw_address = fields.CharField(unique=True, max_length=40)
    banned = fields.BooleanField(default=False)
    nonce = fields.IntField(default=0)

    transfers_receive = fields.ReverseRelation["Transfer"]
    transfers_send = fields.ReverseRelation["Transfer"]
    balances = fields.ReverseRelation["Balance"]

    class Meta:
        table = "service_addresses"
