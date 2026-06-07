from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AggregationResult:
    asset_id: str
    year: int
    count: int


@dataclass(frozen=True)
class PredictionResult:
    seconds: int
    actual: float
    predicted: float


class AnalyticsEnginePort(ABC):
    @abstractmethod
    async def run_aggregation(self, data_source_id: str) -> list[AggregationResult]: ...

    @abstractmethod
    async def run_prediction(
        self, asset_id: str, data_source_id: str
    ) -> list[PredictionResult]: ...
