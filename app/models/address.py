from tortoise import fields
from .base import Base

class Address(Base):
    label = fields.CharField(index=True, unique=True, max_length=64)
    banned = fields.BooleanField(default=False)

    transfers_receive = fields.ReverseRelation["Transfer"]
    transfers_send = fields.ReverseRelation["Transfer"]
    owned_tokens = fields.ReverseRelation["Token"]
    balances = fields.ReverseRelation["Balance"]

    admin_fee_addresses = fields.ReverseRelation["FeeAddress"]
    admin_costs = fields.ReverseRelation["TokenCost"]
    address_unban = fields.ReverseRelation["Unban"]
    admin_unban = fields.ReverseRelation["UnBan"]

    address_ban = fields.ReverseRelation["Ban"]
    admin_ban = fields.ReverseRelation["Ban"]

    index = fields.ReverseRelation["Index"]
    locks = fields.ReverseRelation["Lock"]

    class Meta:
        table = "service_addresses"
