from domain.ports.time_series_repository import TimeSeriesRepositoryPort


class GetPredictionResultsUseCase:
    def __init__(self, ts_repo: TimeSeriesRepositoryPort):
        self._ts_repo = ts_repo

    async def execute(self) -> list[dict]:
        return await self._ts_repo.get_prediction_results()
