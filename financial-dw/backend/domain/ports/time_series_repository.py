from abc import ABC, abstractmethod
from datetime import date

from domain.entities.time_series_point import TimeSeriesPoint


class TimeSeriesRepositoryPort(ABC):
    @abstractmethod
    async def save(self, point: TimeSeriesPoint) -> TimeSeriesPoint: ...

    @abstractmethod
    async def save_batch(self, points: list[TimeSeriesPoint]) -> int: ...

    @abstractmethod
    async def find_latest_by_date_range(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
    ) -> list[TimeSeriesPoint]: ...

    @abstractmethod
    async def get_aggregation_totals(self) -> list[dict]: ...

    @abstractmethod
    async def get_prediction_results(self) -> list[dict]: ...

    @abstractmethod
    async def get_model_metrics(self) -> list[dict]: ...
