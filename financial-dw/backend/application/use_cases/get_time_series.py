from datetime import date

from domain.ports.time_series_repository import TimeSeriesRepositoryPort
from domain.entities.time_series_point import TimeSeriesPoint


class GetTimeSeriesUseCase:
    def __init__(self, ts_repo: TimeSeriesRepositoryPort):
        self._ts_repo = ts_repo

    async def execute(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
    ) -> list[TimeSeriesPoint]:
        return await self._ts_repo.find_latest_by_date_range(
            asset_id, data_source_id, start_date, end_date
        )
