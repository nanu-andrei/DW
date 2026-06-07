from pydantic import BaseModel
from datetime import datetime

from domain.entities.data_source import DataSource


class DataSourceSummaryResponse(BaseModel):
    id: str


class DataSourceDetailResponse(BaseModel):
    id: str
    system_date: datetime
    name: str
    description: str
    attributes: list[str]

    @classmethod
    def from_entity(cls, ds: DataSource) -> "DataSourceDetailResponse":
        return cls(
            id=ds.id,
            system_date=ds.system_date,
            name=ds.name,
            description=ds.description,
            attributes=sorted(ds.attributes),
        )
