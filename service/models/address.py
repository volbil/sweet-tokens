from tortoise import fields
from .base import Base

class Address(Base):
    label = fields.CharField(unique=True, max_length=40)
    banned = fields.BooleanField(default=False)
    nonce = fields.IntField(default=0)  # ToDo: do we need this?

    transfers_receive = fields.ReverseRelation["Transfer"]
    transfers_send = fields.ReverseRelation["Transfer"]
    balances = fields.ReverseRelation["Balance"]

    class Meta:
        table = "service_addresses"
