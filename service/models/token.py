from sqlmodel import Field, Relationship
from pydantic import condecimal
from .base import BaseTable
from typing import Union
from typing import List

class Token(BaseTable, table=True):
    __tablename__ = "service_tokens"

    name: str
    ticker: str
    supply: Union[condecimal(max_digits=28, decimal_places=8), None] = None

    balances: List["Balance"] = Relationship(back_populates="token")
    transfers: List["Transfer"] = Relationship(back_populates="token")
