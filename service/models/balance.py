from sqlmodel import Field, Relationship
from pydantic import condecimal
from .base import BaseTable
from typing import Optional
from typing import Union

class Balance(BaseTable, table=True):
    __tablename__ = "service_balances"

    amount: Union[condecimal(max_digits=28, decimal_places=8), None] = None

    address_id: Optional[int] = Field(default=None, foreign_key="service_addresses.id")
    address: Optional["Address"] = Relationship(back_populates="balances")

    token_id: Optional[int] = Field(default=None, foreign_key="service_tokens.id")
    token: Optional["Token"] = Relationship(back_populates="balances")
