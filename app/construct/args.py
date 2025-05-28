from pydantic import BaseModel, Field
from ..chain import get_chain
from typing import Union
import config

class BuildArgs(BaseModel):
    marker: int = Field(default=get_chain(config.chain)["marker"])
    fee: int = Field(default=get_chain(config.chain)["fee"])
    receive_address: Union[str, None] = Field(default=None)
    send_address: str
    payload: str
