from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timedelta
from pydantic import PlainSerializer
from typing import Annotated
from . import utils
import typing


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

    def serializable_dict(self, **_):
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)


class PaginationData(CustomModel):
    total: int = Field(ge=0, description="Total number of items")
    page: int = Field(ge=1, description="Number of page")
    pages: int = Field(ge=0, description="Total number of pages")


T_s = typing.TypeVar("T_s", bound=CustomModel)


class Paginated(typing.Generic[T_s]):
    """
    Paginated response model generator.

    Usage::

        @router.method("path", response_model=Paginated[ItemModel])
    """

    __models__: dict[str, type["Paginated[typing.Any]"]] = {}

    pagination: PaginationData
    list: list[T_s]

    def __class_getitem__(cls, item_model: type[T_s]) -> type["Paginated[T_s]"]:
        model_name = item_model.__qualname__ + "Pagination"

        if model_name in cls.__models__:
            return cls.__models__[model_name]

        model = typing.cast(
            type["Paginated[T_s]"],
            type(
                model_name,
                (
                    CustomModel,
                    Paginated,
                ),
                dict(
                    __annotations__=dict(
                        pagination=PaginationData, list=list[item_model]
                    ),
                    pagination=Field(description="Information about the pagination"),
                    list=Field(description="List of items"),
                    __module__=__name__,
                ),
            ),
        )

        cls.__models__[model_name] = model

        return model
