from domain.ports.analytics_engine import AnalyticsEnginePort, PredictionResult


class RunPredictionUseCase:
    def __init__(self, analytics: AnalyticsEnginePort):
        self._analytics = analytics

    async def execute(
        self, asset_id: str, data_source_id: str
    ) -> list[PredictionResult]:
        return await self._analytics.run_prediction(asset_id, data_source_id)
