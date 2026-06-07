from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DataSource:
    id: str
    system_date: datetime
    name: str = ""
    description: str = ""
    attributes: set[str] = field(default_factory=set)
