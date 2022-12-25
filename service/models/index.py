from .base import Base, NativeDatetimeField
from tortoise import fields

class Index(Base):
    category = fields.CharField(index=True, max_length=32)
    created = NativeDatetimeField()

    address: fields.ForeignKeyRelation["Address"] = fields.ForeignKeyField(
        "models.Address", related_name="index"
    )

    transfer: fields.ForeignKeyRelation["Transfer"] = fields.ForeignKeyField(
        "models.Transfer", related_name="index",
        on_delete=fields.CASCADE
    )

    token: fields.ForeignKeyRelation["Token"] = fields.ForeignKeyField(
        "models.Token", related_name="index",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "service_index"
