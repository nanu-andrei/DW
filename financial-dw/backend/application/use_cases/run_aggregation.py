from domain.ports.analytics_engine import AnalyticsEnginePort, AggregationResult


class RunAggregationUseCase:
    def __init__(self, analytics: AnalyticsEnginePort):
        self._analytics = analytics

    async def execute(
        self, data_source_id: str
    ) -> list[AggregationResult]:
        return await self._analytics.run_aggregation(data_source_id)
