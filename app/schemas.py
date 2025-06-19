from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from pydantic import PlainSerializer
from typing import Annotated
from . import utils


# Custom Pydantic serializers
datetime_pd = Annotated[
    datetime,
    PlainSerializer(
        lambda x: utils.to_timestamp(x),
        return_type=int,
    ),
]

timedelta_pd = Annotated[
    timedelta,
    PlainSerializer(
        lambda x: int(x.total_seconds()),
        return_type=int,
    ),
]


# Custom Pydantic model
class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
        extra="forbid",
    )

    def serializable_dict(self, **kwargs):
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)
