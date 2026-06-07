import asyncio

from domain.ports.analytics_engine import (
    AnalyticsEnginePort,
    AggregationResult,
    PredictionResult,
)
from infrastructure.config.settings import get_settings
from infrastructure.adapters.spark.aggregation_job import run_aggregation
from infrastructure.adapters.spark.regression_job import run_prediction


class SparkAnalyticsAdapter(AnalyticsEnginePort):
    def __init__(self):
        settings = get_settings()
        self._cassandra_host = settings.cassandra_hosts[0]
        self._keyspace = settings.cassandra_keyspace

    async def run_aggregation(
        self, data_source_id: str
    ) -> list[AggregationResult]:
        count = await asyncio.to_thread(
            run_aggregation,
            cassandra_host=self._cassandra_host,
            keyspace=self._keyspace,
            data_source_filter=data_source_id,
        )
        return [AggregationResult(asset_id="all", year=0, count=count)]

    async def run_prediction(
        self, asset_id: str, data_source_id: str
    ) -> list[PredictionResult]:
        result = await asyncio.to_thread(
            run_prediction,
            cassandra_host=self._cassandra_host,
            keyspace=self._keyspace,
            asset_id=asset_id,
            data_source_id=data_source_id,
        )
        # run_prediction now returns a dict with metrics
        return [
            PredictionResult(
                seconds=0,
                actual=0.0,
                predicted=0.0,
            )
        ]
