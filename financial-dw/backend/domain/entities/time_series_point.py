from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class TimeSeriesPoint:
    asset_id: str
    data_source_id: str
    business_date: date
    business_date_year: int
    system_date: datetime
    values_double: dict[str, float] = field(default_factory=dict)
    values_int: dict[str, int] = field(default_factory=dict)
    values_text: dict[str, str] = field(default_factory=dict)
    deleted: bool = False
