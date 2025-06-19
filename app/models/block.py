from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime
from .base import Base


class Block(Base):
    __tablename__ = "service_blocks"

    hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    height: Mapped[int] = mapped_column(index=True)
    created: Mapped[datetime]
