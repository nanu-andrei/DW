from pydantic import BaseModel
from typing import Any, Optional


class TimeSeriesRecord(BaseModel):
    businessDate: str
    values: dict[str, float | int | str]


class TimeSeriesDataResponse(BaseModel):
    assetId: str
    datasourceId: str
    records: list[TimeSeriesRecord]


class TimeSeriesResponse(BaseModel):
    data: TimeSeriesDataResponse
    attributes: Optional[list[str]] = None
