from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String
from .base import Base


class Address(Base):
    __tablename__ = "service_addresses"

    label: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    banned: Mapped[bool] = mapped_column(default=False)
