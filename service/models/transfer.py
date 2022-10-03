from sqlmodel import Field, Relationship
from pydantic import condecimal
from .base import BaseTable
from typing import Optional
from typing import Union

class Transfer(BaseTable, table=True):
    __tablename__ = "service_transfer"

    amount: Union[condecimal(max_digits=28, decimal_places=8), None] = None
    txid: str

    token_id: Optional[int] = Field(default=None, foreign_key="service_tokens.id")
    token: Optional["Token"] = Relationship(back_populates="transfers")

    sender_id: Optional[int] = Field(default=None, foreign_key="service_addresses.id")
    sender: Optional["Address"] = Relationship(
        back_populates="transfers_send",
        sa_relationship_kwargs=dict(
            primaryjoin="Address.id==Transfer.sender_id"
        )
    )

    receiver_id: Optional[int] = Field(default=None, foreign_key="service_addresses.id")
    receiver: Optional["Address"] = Relationship(
        back_populates="transfers_receive",
        sa_relationship_kwargs=dict(
            primaryjoin="Address.id==Transfer.receiver_id"
        )
    )
