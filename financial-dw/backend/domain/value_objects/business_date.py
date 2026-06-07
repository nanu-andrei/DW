from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BusinessDate:
    value: date

    @property
    def year(self) -> int:
        return self.value.year

    def __str__(self) -> str:
        return self.value.isoformat()
