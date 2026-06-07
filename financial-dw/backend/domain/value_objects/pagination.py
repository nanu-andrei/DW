from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PageRequest:
    offset: int = 0
    limit: int = 20


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    offset: int
    limit: int
    total: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total
