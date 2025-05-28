from tortoise import fields
from .base import Base

class Unban(Base):
    txid = fields.CharField(index=True, unique=True, max_length=64)

    block: fields.ForeignKeyRelation["Block"] = fields.ForeignKeyField(
        "models.Block", related_name="unbans",
        on_delete=fields.CASCADE
    )

    admin: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="admin_unban"
    )

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="address_unban"
    )

    class Meta:
        table = "service_unbans"
