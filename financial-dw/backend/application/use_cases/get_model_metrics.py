from domain.ports.time_series_repository import TimeSeriesRepositoryPort


class GetModelMetricsUseCase:
    def __init__(self, ts_repo: TimeSeriesRepositoryPort):
        self._ts_repo = ts_repo

    async def execute(self) -> list[dict]:
        return await self._ts_repo.get_model_metrics()
