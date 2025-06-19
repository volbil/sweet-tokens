from app.schemas import CustomModel
from pydantic import Field


class BuildArgs(CustomModel):
    receive_address: str | None = Field(default=None)
    send_address: str
    payload: str
    marker: int
    fee: int
