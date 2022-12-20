from tortoise import fields
from .base import Base

class Ban(Base):
    txid = fields.CharField(index=True, unique=True, max_length=64)

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        "models.Block", related_name="bans",
        on_delete=fields.CASCADE
    )

    admin: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="admin_ban"
    )

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="address_ban"
    )

    class Meta:
        table = "service_bans"
