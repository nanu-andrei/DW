from pydantic import BaseModel
from typing import Any


class PaginatedResponse(BaseModel):
    items: list[Any]
    offset: int
    limit: int
    total: int
    has_next: bool


class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 500
