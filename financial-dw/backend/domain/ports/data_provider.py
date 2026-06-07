from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawTimeSeriesPage:
    records: list[dict]
    columns: list[str]
    next_cursor: str | None
    source_id: str
    dataset_code: str


class DataProviderPort(ABC):
    @abstractmethod
    async def fetch_dataset(
        self,
        dataset_code: str,
        cursor: str | None = None,
        page_size: int = 100,
    ) -> RawTimeSeriesPage: ...

    @abstractmethod
    def get_provider_id(self) -> str: ...
