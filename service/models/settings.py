from tortoise import fields
from .base import Base

class Settings(Base):
    current_height = fields.IntField(default=0)

    class Meta:
        table = "service_settings"
