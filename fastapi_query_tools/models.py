from __future__ import annotations
from pydantic import BaseModel, Field
from fastapi import Query
from .enums import Order
from typing import Any


class QueryModel(BaseModel):
    q: Any | None = Field(Query(None, description="The value used to filter"))
    sort_by: str | None = Field(Query(None, description="The column to sort/filter by"))
    order: Order | None = Field(
        Query(
            None,
            description="The order to sort by",
            example="asc",
        )
    )
